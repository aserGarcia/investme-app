
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ml_agents.GRU_Manager import GRU_Manager
from mv_optimization import MVOptimization
import sys

sys.path.insert(1, '../data_collection')

from collect_data_helper import get_stock_prices

BATCH_SIZE = 64
EPOCHS = 100
T = 5 #number of past prices for T timsesteps (5 days)
test_time_window = 50 #50 trading days (10 weeks)

#------------------------------------------------
#           Sharpe Ratio Comarison
#------------------------------------------------

shp_chosen = pd.read_csv('portfolio_data/sharpe_chosen_stocks.csv')
shp_stock_ts = get_stock_prices(shp_chosen['Stocks']).reset_index()

train_end_idx = len(shp_stock_ts)-test_time_window
shp_stock_train = shp_stock_ts.truncate(after=train_end_idx).set_index('date')
shp_stock_test = shp_stock_ts.truncate(before=train_end_idx+1).set_index('date')

name="sharpe"
gru_shp = GRU_Manager(shp_stock_train,data_name=name,epochs=EPOCHS,batch_size=BATCH_SIZE)
gru_shp.save_true_and_predicted()

dates = [shp_stock_train.index[-1].replace("2020-","")]
mv_cum_returns = [0]
gru_cum_returns = [0]
mv_past_whts=np.full(shp_stock_test.shape[1],1.0/shp_stock_test.shape[1])
gru_past_whts = np.full(shp_stock_test.shape[1],1.0/shp_stock_test.shape[1])

for i in range(T,len(shp_stock_test),T):
    
    prices_window = shp_stock_test.iloc[i-T:i]
    eval_price = shp_stock_test.iloc[i-T:i+1]
    
    prices_returns = np.nan_to_num(eval_price.pct_change().iloc[-1].to_numpy())

    dates.append(prices_window.index[-1].replace("2020-",""))

    #predictis current time step
    prediction = gru_shp.model.predict(np.expand_dims(prices_window.to_numpy(),axis=0))
    pred_df = pd.DataFrame(prediction,columns=shp_stock_test.columns)
    gru_whts = gru_shp.get_weights(pred_df)['Weights'].to_numpy()

    gru_alloc_value = np.dot(gru_whts.T, prices_returns)
    gru_cum_returns.append(gru_cum_returns[-1]+gru_alloc_value)

    
    #Calculating cumulitive returns on mv allocation
    
    mv_shp = MVOptimization(prices_window,name='sharpe_test')
    
    mv_alloc_value = np.dot(mv_past_whts.T, prices_returns)

    mv_cum_returns.append(mv_cum_returns[-1]+mv_alloc_value)
    mv_whts = np.array(mv_shp.bestSharpeRatio()['x'])
    mv_whts[mv_whts<1e-5]=0.0
    mv_past_whts=mv_whts


#clearing memory on GPU
del gru_shp

#------------------------------------------------
#           Minimum Variance Comparison
#------------------------------------------------
mr_chosen = pd.read_csv('portfolio_data/minrisk_chosen_stocks.csv')
mr_stock_ts = get_stock_prices(mr_chosen['Stocks']).reset_index()

train_end_idx = len(mr_stock_ts)-test_time_window
mr_stock_train = mr_stock_ts.truncate(after=train_end_idx).set_index('date')
mr_stock_test = mr_stock_ts.truncate(before=train_end_idx+1).set_index('date')

name="minimumRisk"
gru_minvar = GRU_Manager(mr_stock_train,data_name=name,epochs=EPOCHS,batch_size=BATCH_SIZE)
gru_minvar.save_true_and_predicted()

dates = [mr_stock_train.index[-1].replace("2020-","")]
mr_cum_returns = [0]
gru_mr_cum_returns = [0]
mr_past_whts=np.full(mr_stock_test.shape[1],1.0/mr_stock_test.shape[1])
gru_past_whts = np.full(mr_stock_test.shape[1],1.0/mr_stock_test.shape[1])

for i in range(T,len(mr_stock_test),T):
    
    prices_window = mr_stock_test.iloc[i-T:i]
    eval_price = mr_stock_test.iloc[i-T:i+1]
    
    prices_returns = np.nan_to_num(eval_price.pct_change().iloc[-1].to_numpy())

    dates.append(prices_window.index[-1].replace("2020-",""))

    #predictis current time step
    prediction = gru_minvar.model.predict(np.expand_dims(prices_window.to_numpy(),axis=0))
    pred_df = pd.DataFrame(prediction,columns=mr_stock_test.columns)
    gru_whts = gru_minvar.get_weights(pred_df)['Weights'].to_numpy()

    gru_alloc_value = np.dot(gru_whts.T, prices_returns)
    gru_mr_cum_returns.append(gru_mr_cum_returns[-1]+gru_alloc_value)

    
    #Calculating cumulitive returns on mv allocation
    
    mv_mr = MVOptimization(prices_window,name='minvar')
    
    mr_alloc_value = np.dot(mr_past_whts.T, prices_returns)

    mr_cum_returns.append(mr_cum_returns[-1]+mr_alloc_value)
    mr_whts = np.array(mv_mr.bestVariance()['x'])
    mr_whts[mr_whts<1e-5]=0.0
    mr_past_whts=mr_whts




plt.figure(1,figsize=(8.0,10.0))

plt.subplot(211)
plt.plot(dates,gru_cum_returns,label='gru-sharpe')
plt.plot(dates,mv_cum_returns,label='mv-sharpe')
plt.plot(dates,gru_mr_cum_returns,label='gru-minvar')
plt.plot(dates,mr_cum_returns,label='optimal-minvar')
plt.xlabel('Dates: Spring 2020')
plt.ylabel('Cumulative returns')
plt.title("Comparison on 10 Weeks Cumulative Returns")
plt.legend()


plt.subplot(212)
plt.bar(dates, gru_cum_returns,label='gru-sharpe')
plt.bar(dates, mv_cum_returns, label='mv-sharpe')
plt.bar(dates, gru_mr_cum_returns,label='gru-minvar')
plt.bar(dates, mr_cum_returns, label='mv-minvar')
plt.xlabel('Dates: Spring 2020')
plt.ylabel('Cumulative returns')
plt.title("Comparison on 10 Weeks Cumulative Returns")
plt.legend()
plt.title("Comparison on 10 Weeks Cumulative Returns")

plt.savefig('compare_graphs/mivar_comparison.png')
