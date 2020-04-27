from cassandra.cluster import Cluster
import pandas as pd
import matplotlib.pyplot as plt
from ts_graph_tool import ts_slider
from mv_optimization import MVOptimization
import numpy as np
from ml_agents.GRU_Manager import GRU_Manager

#-----------------------------------------------------#
#                  Gathering Data                     #       
#-----------------------------------------------------#

#connecting to local cassandra database
cluster = Cluster(contact_points=['127.0.0.1'])
#setting session
cdb_sess = cluster.connect()
cdb_sess.execute("use sp500")

#dataframe calling sector averages
def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)

#making dataframe after query from local cassandra DB
cdb_sess.row_factory = pandas_factory
sector_avg = cdb_sess.execute("select * from sector_avg")
sec_df = sector_avg._current_rows

sec_df = sec_df.sort_values(by='date').set_index('date')
#sec_df.to_csv("SectorPrices.csv")
#exit()
#-----------------------------------------------------#
#                  Sector Analysis                    #       
#-----------------------------------------------------#
gru = GRU_Manager(sec_df)
#gru.plot_train_history()
gru.plot_predicted()

#mv = MVOptimization(sec_df, "sectors")
#mv.plot_portfolios()
#mv.plot_mv()
