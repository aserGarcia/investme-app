 
from cassandra.cluster import Cluster
import pandas as pd
import matplotlib.pyplot as plt
from ts_graph_tool import ts_slider
from mv_optimization import MVOptimization
import numpy as np

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

#interactive plot
#ts_slider(sec_df)
w = np.full(sec_df.shape[1], 1.0/sec_df.shape[1])
m_ret = sec_df.pct_change().mean(axis=0)
cov_mat = sec_df.cov()

mv = MVOptimization(sec_df)
#ra = mv.optRiskAversion(alpha=10)
#sr = mv.optSharpeRatio()
#v = mv.optVariance(0.3)
#print(v,ra)
mv.plot_mv()
#mv.plot_pctChange()