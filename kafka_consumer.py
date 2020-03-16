from kafka import KafkaConsumer



#tuple because consumer expects hashable type
topics = ("TSLA", "GOOGL")

kafka_broker = '127.0.0.1:9092'

#TODO: cassandra connect, store accordingly

if __name__ == "__main__":
	consumer = KafkaConsumer(bootstrap_servers=kafka_broker)
	consumer.subscribe(topics)

	for msg in consumer:
		print(msg.value)

