import logging
import pandas as pd
import argparse
from cassandra.cluster import Cluster, BatchStatement
from kafka import KafkaConsumer


class CassandraCluster:
	
	def __init__(self, contact, keyspace='sp500'):
		self.cluster = Cluster(contact_points=[contact])
		self.session = self.cluster.connect()
		self.keyspace = keyspace
		self.log = None

	def __del__(self):
		self.session.shutdown()

	def getSession(self):
		'''
		Desc - Returns the current session of the Cassandra database
		'''
		return self.session
	
	def setLogger(self):
		'''
		Desc - creates a logger to output and log any activity.
		'''
		logger = logging.getLogger('cassandra')
		logger_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		log = logging.StreamHandler()
		logging.basicConfig(filename="debug.log", filemode='w', level=logging.DEBUG)
		log.setFormatter(logger_format)
		logger.addHandler(log)
		logger.info('Created logger...')
		self.log = logger

	def createKeyspace(self, keyspace='sp500'):
		'''
		Desc - creating a keyspace, "keypace" holds the column families for the database.
				it will create a new keyspace if it does not currently exist.
		@param - keyspace: the name to set the keypace to
		'''
		keyspace = self.keyspace
		self.session.execute("""
						CREATE KEYSPACE IF NOT EXISTS %s
						WITH replication = {'class':'SimpleStrategy','replication_factor':'3'};
						"""%keyspace)

		self.log.info('setting keyspace...')
		self.session.execute('USE %s'%keyspace)
		print(self.cluster.metadata.keyspaces)
		
	def createTable(self, table_name):
		'''
		Desc - create a table if it is not created yet
		@param - table_name: the name of the table to be created
		'''
		self.session.execute("""
							CREATE TABLE IF NOT EXISTS %s (date timestamp PRIMARY KEY,
												open float,
												high float,
												low float,
												close float,
												volume int);
												
							"""%table_name)
		self.log.info(table_name, " table created...")

	def insert_data(self, data, table_name):
		'''
		Desc - insert data into a specified table by batches (expecting over 500 entries at once)
		@param - data: list of tuples containing data needing to be inserted
		@param - table_name: the name of the table to insert the data
		'''
		try:
			sql_prep = self.session.prepare("""
					INSERT INTO %s (date, open, high, low, close, volume) VALUES (?,?,?,?,?,?);
				"""%table_name)
			batch = BatchStatement()
			for row_tuple in data:
				batch.add(sql_prep, row_tuple)
			self.session.execute(batch)
			self.log.info('Batch insert complete...')
		except:
			self.log.info("ERROR: Could not append to table...")
	
	def selectData(self, table_name, range):
		'''
		Desc - select data from a range of timestamps in the specified table name.
		@param - table_name: the name of the table to retrieve data from
		@param - range: list of keys to retrive data from. Format string date mm-dd-yyyy
		'''
		try:
			rows = self.session.execute("SELECT * FROM %s WHERE date > %s AND date < %s;"%(table_name,range[0],range[1]))
			self.log.info("Querying %s WHERE date > %s AND date < %s;%(table_name,range[0],range[1]")
			return rows
		except:
			self.log.info("ERROR: Could not fetch query...")

if __name__ == "__main__":

	# Local connection points
	kafka_broker = '127.0.0.1:9092'
	
	#setup args
	parser = argparse.ArgumentParser()
	parser.add_argument('csv_file', help='CSV file of company list (ID, Symbol, Name, Sector)')

	#parse args
	args = parser.parse_args()
	filename = args.csv_file

	#read company stock meta-data file
	stocks = pd.read_csv(filename)

	#setup connections
	consumer = KafkaConsumer(bootstrap_servers=kafka_broker)
	consumer.subscribe(tuple(stocks['Symbol']))
	cassDB = CassandraCluster('127.0.0.1')
	cassDB.setLogger()

'''
	#prep database
	cassDB.createKeyspace()
	for new_table in stocks['Symbol']:
		cassDB.createTable(new_table)

	#send data from kafka to database
	for msg in consumer:
		#company stock symbol for table
		symbol = list(msg.keys())[0]
		#msg[symbol] returns list of tuples
		cassDB.insert_data(msg[symbol], symbol)
'''

	
