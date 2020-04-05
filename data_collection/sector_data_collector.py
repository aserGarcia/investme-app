"""
April 04, 2020
This prorgam collects data specific to sectors in the SP500 index.
New tables will be created for respective sectors using the 
closing price for data and sector stocks for columns
"""

#start of main program
from cassandra_setup import CassandraCluster
import pandas as pd

#--------python pandas side------
def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)

#importing sp500 index: cols: Symbol | Sector
sp5 = pd.read_csv("SP500.csv",usecols=[1,3])
#print(sp5.head())

#dictionary with indexes per sector
sp5_secIndx = sp5.groupby(['Sector']).groups
sp5sec = pd.DataFrame(columns=sp5_secIndx.keys())

#sp5sec contains sectors as columns and stocks to that sector as rows
for sector in sp5_secIndx.keys():
    idx = sp5_secIndx[sector]
    sp5sec[sector] = sp5.iloc[idx].reset_index().Symbol



#-------cassandra side-------------
#connecting to local cassandra database
cdb = CassandraCluster('127.0.0.1')
cdb.setLogger()


#setting keyspace
cdb.session.execute("use sp500")
cdb.session.row_factory = pandas_factory

#closing price time series
sp5secTS = pd.DataFrame()

for col in sp5sec.columns:
    stocks = sp5sec[col].dropna()
    sec_df = pd.DataFrame()

    for stock in stocks:
        if "." in stock:
            stock = stock.replace(".","")
        result = cdb.session.execute("select * from "+stock)
        df = result._current_rows

        #setting index as date to graph time series
        df=df.sort_values(by='date')[['date','close']].set_index('date')
    
        #renaming to current stock name
        df = df.rename(columns={'close':stock})
        sec_df = pd.concat([sec_df,df], axis=1)

    #compute average across company stocks for sector
    avg_column = col.replace(" ","_")+'_AVG'
    sec_df[avg_column] = sec_df.mean(axis=1)
    sp5secTS = pd.concat([sp5secTS,sec_df[avg_column]], axis=1)
    #print(sp5secTS.head())

    #preparing table to be appended
    table_name = col.replace(" ","_")
    colnames = sec_df.columns[:-1]
    separator = " float, "
    table_config = separator.join(colnames)
    table_config += " float"
    create_query = "create table if not exists %s (date text primary key, %s);"%(table_name,table_config)
    cdb.session.execute(create_query)
    
    #insert stocks of current sector into table
    query = "insert into %s (date, %s) values (%s)"%(table_name, ','.join(colnames),
                                                 ','.join("?"*(len(colnames)+1)))
    print("Finished INSERT: ",table_name)
    prep = cdb.session.prepare(query)
    
    for date in sec_df.index:
        cdb.session.execute(prep, [date]+list(sec_df.loc[date])[:-1])
 
#insert averages of sectors into table
separator = " float, "
table_config = separator.join(sp5secTS.columns)
table_config += " float"
cdb.session.execute("create table if not exists sector_avg (date text primary key, %s);"%table_config)
query = "insert into sector_avg (date, %s) values (%s)"%(','.join(sp5secTS.columns),
                                                 ','.join("?"*(len(sp5secTS.columns)+1)))
prep = cdb.session.prepare(query)
for date in sec_df.index:
    cdb.session.execute(prep, tuple([date]+list(sp5secTS.loc[date])))
