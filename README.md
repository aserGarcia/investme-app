# **Invest Me App-2020**

## **Repository Structure**
There are three main folders for this repository.  
1. Data Collection - stream processing stock data
2. Asset Allocation - portfolio selection
3. Dashboard  - portfolio visualization
  
  
## Data Collection  
This directory contains the scripts to instantiate a producer and consumer for Kafka and storing it in a NoSQL database using Cassandra.  

**Apache Kafka**  
Apache Kafka is a system to process streams through a message subscription distributed streaming platform. This means streams are processed as topics that are sent through messages. The platform is built to be fault tolerant which as a design choice for this project due to the importance of valid data for asset management. In addition, Kafka is scalable leaving the door open to high-frequency trading. **Kafka should be setup locally for these scripts**.  
  
**Cassandra**  
Cassandra is a NoSQL database used for fast read and writes to store data in tables. Cassandra was a design choice due to its linear scalability and speed. **A local instance of Cassandra is needed for these scripts**  

**Alpha Vantage**  
Alpha Vantage is an API for stock data. The cap for API calls in the free version is 500/day at 5 calls/minute. In the future, Quandl will be used for stock data since it has a higher API call cap.

**Scripts**  
The **kafka_consumer.py** must be run first in order to be ready for the topics the producer will be streaming.  
Run as below in genome terminal (Linux):  
```
~$ python kafka_consumer.py
```  
The **kafka_producer.py** file allows for calls to Alpha Vantage by adding arguments to the  
call on the terminal. 
1. Update Flag - Gather data from the date the companies went public
2. CSV File - CSV file of assets to fetch data
3. Row Start - Row of CSV file to start at
```
~$ python kafka_producer.py <Update Flag: Bool> <CSV file> <Row Start: Int>
```

Cassandra will store the data in an unordered manner for the time series. 
![cassandra1](/readme_images/cassandra_tables.png)
![cassandra2](/readme_images/ebaydataset_example.png)  

## Asset Allocation  
**Strategy**  
In this project, a top-down investment strategy was implemented. Stock choices are performed by first analyzing each sector in the SP500 and then further analyzing the stocks in each sector. 

**Scripts**  
Scripts for initializing and training both machine learning and statistical models are stored in the directory **asset_allocation**.  
**sector_analysis.py** must be run first in order to create portfolios on the sectors. 
```
~$ python sector_analysis.py
```
This will create a csv file in the folder portfolio_data with weights based on both strategies,  
minimum risk and sharpe ratio. The only output to the terminal from running this script should  
be the sum of the weights which should be close to 1.0.  
![sectorcsv](/readme_images/csv_sectors.png)
This script should also produce the weights for each stock in a sector adjusted for the total  
investment in that sector.  
![sectorstocks](/readme_images/sectorstockweights.png) 
**Asset management**  
To manage the allocated assets run **compare_methods.py** which will separate the training and testing data for the  
10 week challenge on both models.  
This script produces the models and saves them to the **models** folder. It produces comparison graphs on cumulative returns, how much wealth is accumulated over time, and saves them to the **compare_graphs** folder. The GRU models save their predictions along with the truth for the validation data they were given in the ml_data directory.  
![admStock](/readme_images/admstock.png) 
![mkcStock](/readme_images/mkcstock.png) 
**Dashboard**  
The final directory is the dashboard that shows the asset allocations. This can be run by  
executing the script **make_dash.py**  
```
~$ python make_dash.py
```
This will open up a local host and would just have to click  
the link to see.  
![dash](/readme_images/dashboard.png) 
