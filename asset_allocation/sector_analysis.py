from cassandra.cluster import Cluster
import pandas as pd
import matplotlib.pyplot as plt
import sys

sys.path.insert(1, '../data_collection')


from collect_data_helper import get_stock_prices
from mv_optimization import MVOptimization
import numpy as np

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
sec_df.to_csv("portfolio_data/sector_prices.csv")

#-----------------------------------------------------#
#                  Sector Analysis                    #       
#-----------------------------------------------------#


mv = MVOptimization(sec_df, "sectors")
mv.buildPortfolios()


#-----------------------------------------------------#
#                  Stock Analysis                     #       
#-----------------------------------------------------#
weights = pd.read_csv('portfolio_data/weights_sectors.csv')


#grabbing stocks for best Sharpe Ratio portfolio
shp_invest = weights[weights['Sharpe Ratio']>1e-5][['Stocks','Sharpe Ratio']]

#grabbing stocks for Minimum Variance Portfolio
minvar_invest = weights[weights['Minimum Risk']>1e-5][['Stocks','Minimum Risk']]

#importing sp500 index: cols: Symbol | Sector
sp5 = pd.read_csv("../data_collection/SP500.csv",usecols=[1,3])

#dictionary with indexes per sector
sp5_secIndx = sp5.groupby(['Sector']).groups
sp5sec = pd.DataFrame(columns=sp5_secIndx.keys())

#sp5sec contains sectors as columns and stocks to that sector as rows
for sector in sp5_secIndx.keys():
    idx = sp5_secIndx[sector]
    sp5sec[sector] = sp5.iloc[idx].reset_index().Symbol

#matching casing with mv optimization algorithm
sp5sec.columns = [n.lower() for n in sp5sec.columns]


sharpe_portfolio = pd.DataFrame()
minrisk_portfolio = pd.DataFrame()

for sector in sp5sec.columns:
    try: 
        w_df = pd.read_csv('portfolio_data/weights_'+sector+'.csv')
    except:
        stk = get_stock_prices(sp5sec[sector].dropna())
        mv = MVOptimization(stk, sector)
        mv.buildPortfolios()
    wf_df = pd.read_csv('portfolio_data/weights_'+sector+'.csv')
    shp_stk = w_df[w_df['Sharpe Ratio']>1e-5][['Stocks','Sharpe Ratio']]
    mv_stk = w_df[w_df['Minimum Risk']>1e-5][['Stocks','Minimum Risk']]

    #portioning on sector investment for best sharpe ratio    
    sector_weight = shp_invest[shp_invest['Stocks']==sector]['Sharpe Ratio']
    if len(sector_weight)!=0:
        shp_stk['Sharpe Ratio'] *= float(sector_weight)
        if sharpe_portfolio.empty:
            sharpe_portfolio = shp_stk.copy()
        else:
            sharpe_portfolio = sharpe_portfolio.append(shp_stk,ignore_index=True)
    
    #portioning on sector investment for minimum risk
    sector_weight = minvar_invest[minvar_invest['Stocks']==sector]['Minimum Risk']
    if len(sector_weight)!=0:
        mv_stk['Minimum Risk'] *= float(sector_weight)
        if minrisk_portfolio.empty:
            minrisk_portfolio = mv_stk.copy()
        else:
            minrisk_portfolio = minrisk_portfolio.append(mv_stk,ignore_index=True)

sharpe_portfolio.columns = ['Stocks','Weights']
minrisk_portfolio.columns = ['Stocks','Weights']

sharpe_portfolio.to_csv('portfolio_data/sharpe_chosen_stocks.csv',index=False)
minrisk_portfolio.to_csv('portfolio_data/minrisk_chosen_stocks.csv',index=False)

print('''Checking Weight Sum...\n \
        Sharpe Portfolio: {}\n \
        Minimum Risk: {}'''.format(sharpe_portfolio['Weights'].sum(),minrisk_portfolio['Weights'].sum()))




