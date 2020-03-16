import logging
from cassandra.cluster import Cluster
from Kafka import KafkaConsumer

#dictionary of {'ticker_name' : {'name': company_name, 'sector': sector}}
sp500 = {}
with open('SP500.csv', 'r') as spFile:
	for row in spFile:
		row_list = row.strip('\n').split(',')
		sp500[row_list[0]] = {'name':row_list[1], 'sector':row_list[2]}

kafka_broker = '127.0.0.1:9092'
cassandra_session = '127.0.0.1:9042'

class CassandraCluster:
	
	def __init__(self, index_filename, session=None, keyspace='sp500'):
		self.cluster = None
		self.session = session
		self.keyspace = keyspace
		self.log = None

	def __del__(self):
		self.cluster.shutdown()
		
	def createSession(self):
		self.cluster = Cluster(['localhost'])
		self.session = self.cluster.connect(self.keyspace)

	def getSession(self):
		return self.session
	
	def setLogger(self):
		format = logging.Formatter("%(asciitime)s [%(levelname)s] %(name)s: %(message)s")
		logging.basicConfig(format=logger_format)
		log = logging.getLogger()
		log.setLevel('INFO')
		self.log = log

	def createKeyspace(self, keyspace):
		self.session.execute("""
						CREATE KEYSPACE IF NOT EXIST %s
						WITH replication = {'class':'SimpleStrategy',
											'replication_factor':3}
						"""%keyspace)

		self.log.info('setting keyspace...')
		self.session.set_keyspace(keyspace)
		
	def createTable(self, table_name):
		self.session.execute("""
							CREATE TABLE IF NOT EXIST %s (date timestamp PRIMARY KEY,
												open float,
												high float,
												low float,
												close float,
												volume int);
												
							"""%table_name)
		self.log.info(table_name, " table created...")

	def insert_data(self, data):
	#TODO: insert data	
		
if __name__ == "__main__":
	
	#setup command-line arguments
	parser = argparse.ArgumentParser()
	parser.add_argument('index_filename', help='csv file of company list (ticker, name, sector)')

	#parse command-line arguments
	args = parser.parse_args()
	index_filename = args.index_filename

	consumer = KafkaConsumer(bootstrap_servers=kafka_broker)
	consumer.subscribe(tuple(sp500.keys()))

	
