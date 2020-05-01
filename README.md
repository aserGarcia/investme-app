# **portfolioManager-2020**

# Repository Structure  
There are three main folders for this repository. 
**Data Collection**  
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
![cassandra1](/readme_images/cassandra_tables.png)
![cassandra2](/readme_images/ebaydataset_example.png)  

**Asset Allocation**  
In the folder for asset_allocation exist both the scripts for creating models in the  
machine learning and statistical methods.  
sector_analysis.py must be run first in order to create portfolios on the sectors. 
This will create a csv file in the folder portfolio_data with weights based on both strategies,  
minimum risk and sharpe ratio. The only output to the terminal from running this script should  
be the sum of the weights which should be close to 1.0.  
![sectorcsv](/readme_images/csv_sectors.png)
This script should also produce the weights for each stock in a sector adjusted for the total  
investment in that sector.  
![sectorstocks](/readme_images/sectorstockweights.png) 
Afterward, we can run compare_methods.py which will separate the training and testing data for the  
10 week challenge on both models.  
This script produces the models and saves them to the models folder. It produces graphs and saves  
them to the compare_graphs folder. The GRU models save their predictions along with the truth for   
the validation data they were given in the ml_data directory.  
![admStock](/readme_images/admstock.png) 
![mkcStock](/readme_images/mkcstock.png) 
**Dashboard**  
The final directory is the dashboard that shows the asset allocations. This can be run by  
executing the script make_dash.py This will open up a local host and would just have to click  
the link to see.  
![dash](/readme_images/dashboard.png) 