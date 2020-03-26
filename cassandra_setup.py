import logging
import pandas as pd
import argparse
from cassandra.cluster import Cluster, BatchStatement
from kafka import KafkaConsumer

# Local connection points
kafka_broker = '127.0.0.1:9092'
cassandra_session = '127.0.0.1:9042'

class CassandraCluster:
	
	def __init__(self, indx_filename, session=None, keyspace='sp500'):
		self.cluster = None
		self.index_filename = indx_filename
		self.session = session
		self.keyspace = keyspace
		self.log = None

	def __del__(self):
		self.cluster.shutdown()
		
	def createSession(self):
		'''
		Desc - Connects to the currently running cluster of cassandra on the local computer
		'''
		self.cluster = Cluster(['localhost'])
		self.session = self.cluster.connect(self.keyspace)

	def getSession(self):
		'''
		Desc - Returns the current session of the Cassandra database
		'''
		return self.session
	
	def setLogger(self):
		'''
		Desc - creates a logger to output and log any activity.
		'''
		logger_format = logging.Formatter("%(asciitime)s [%(levelname)s] %(name)s: %(message)s")
		logging.basicConfig(format=logger_format)
		log = logging.getLogger()
		log.setLevel('INFO')
		self.log = log

	def createKeyspace(self, keyspace):
		'''
		Desc - creating a keyspace, "keypace" holds the column families for the database.
				it will create a new keyspace if it does not currently exist.
		@param - keyspace: the name to set the keypace to
		'''
		self.session.execute("""
						CREATE KEYSPACE IF NOT EXIST %s
						WITH replication = {'class':'SimpleStrategy',
											'replication_factor':3}
						"""%keyspace)

		self.log.info('setting keyspace...')
		self.session.set_keyspace(keyspace)
		
	def createTable(self, table_name):
		'''
		Desc - create a table if it is not created yet
		@param - table_name: the name of the table to be created
		'''
		self.session.execute("""
							CREATE TABLE IF NOT EXIST %s (date timestamp PRIMARY KEY,
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
		sql_prep = self.session.prepare("""
					INSERT INTO %s (date, open, high, low, close, volume) VALUES (?,?,?,?,?,?)
				"""%table_name)
		batch = BatchStatement()
		for row_tuple in data:
			batch.add(sql_prep, row_tuple)
		self.session.execute(batch)
		self.log.info('Batch insert complete...')

	def appendTable(self, data, table_name):
		'''
		Desc - append data row to a specified table
		@param - data: list of tuples with data needing to be inserted
		@param - table_name: the name of the table to insert the data
		'''
		self.session.execute("""
							INSERT INTO %s (date, open, high, low, close, volume) 
							VALUES (?,?,?,?,?,?)
							"""%table_name)
		self.log.info('Inserted into table...')
	
	def selectData(self, table_name, range):
		'''
		Desc - select data from a range of timestamps in the specified table name.
		@param - table_name: the name of the table to retrieve data from
		@param - range: list of keys to retrive data from. Format date mm-dd-yyyy
		'''
		


if __name__ == "__main__":
	
	#setup command-line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('index_filename', help='csv file of company list (ticker, name, sector)')

	#parse command-line arguments
	args = parser.parse_args()
	index_filename = args.index_filename

	stocks = pd.read_csv("SP500.csv")

	consumer = KafkaConsumer(bootstrap_servers=kafka_broker)
	consumer.subscribe(tuple(stocks['Symbol']))

	cassDB = CassandraCluster(indx_filename = index_filename)

	


	
