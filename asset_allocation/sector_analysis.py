 
from cassandra.cluster import Cluster
import pandas as pd
import matplotlib.pyplot as plt

#connecting to local cassandra database
cluster = Cluster(contact_points=['127.0.0.1'])
#setting session
cdb_sess = cluster.connect()
cdb_sess.execute("use sp500")

#dataframe calling sector averages
def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)

cdb_sess.row_factory = pandas_factory
sector_avg = cdb_sess.execute("select * from sector_avg")
sec_df = sector_avg._current_rows
sec_df = sec_df.sort_values(by='date').set_index('date')
#print(sec_df.head())

#plotting with seaborn
lines = sec_df.plot.line(title="Sector Averages",colormap="viridis")
#plt.axes(lines.set_facecolor((0.0,0.0,0.0)))
plt.axes(lines)
plt.savefig("sector_analysis_graphs/sector_2000-20.png")