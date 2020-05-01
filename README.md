# portfolioManager-2020

**Repository Structure**  
There are three main folders for this repository. 
The first that would be needed to run is the data_collection folder.  
This folder contains the scripts to instantiate a producer and consumer for kafka.  
The kafka_consumer.py must be run first in order to be ready for the topics the producer will  
be streaming. An argument for the topics to be listening to needs to be pased to the execution  
of the script.  
The kafka_producer.py file allows for calls to Alpha Vantage by adding arguments to the  
call on the terminal. This includes the update were the historical stocks are considered,  
the csv file of the stocks to get data for, and the start of the row in the csv file (for saving time)  
After running this we can see our database using the cqlsh terminal command that connects  
to the local cassandra cluster.  

Afterward the local Cassandra cluster which looks like below:  
We can look up tables with SQL like commands to see our data.
![cassandra1](images/cassandra_tables.png)
![cassandra2](images/ebaydataset_example.png)