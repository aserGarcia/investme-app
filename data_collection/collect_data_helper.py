
import pandas as pd
from cassandra_setup import CassandraCluster

#--------python pandas side------
def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)

def get_stock_prices(stocks_df):

    #-------cassandra side-------------
    #connecting to local cassandra database
    cdb = CassandraCluster('127.0.0.1')
    cdb.setLogger()

    #setting keyspace
    cdb.session.execute("use sp500")
    cdb.session.row_factory = pandas_factory

    first_set = cdb.session.execute("select * from "+stocks_df.iloc[0])
    sec_ts = first_set._current_rows.sort_values(by='date')[['date','close']].set_index('date')
    sec_ts = sec_ts.rename(columns={'close':stocks_df.iloc[0]})

    for stock in stocks_df[1:,]:
            if "." in stock:
                stock = stock.replace(".","")
            result = cdb.session.execute("select * from "+stock)
            df = result._current_rows
            
            #setting index as date to graph time series
            df=df.sort_values(by='date')[['date','close']].set_index('date')
            #renaming to current stock name
            df = df.rename(columns={'close':stock})
            sec_ts = sec_ts.join(df)
    del cdb
    return sec_ts.fillna(0)