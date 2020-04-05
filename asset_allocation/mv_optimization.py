import pandas as pd 
import scipy as scp
import seaborn as sns
import numpy as np

class MVOptimization:

    def __init__(self, stock_df):
        '''
        Desc - constructor for mean variance on stocks
        @param stock_df -  pandas df stock time series
        '''
        # M stocks for T time window timeseries
        # Must contain 'Symbol' and 'Sector'
        self.stock_df = stock_df
        self.cov = stock_df.cov()
        self.mean = stock_df.mean(axis=0)
        self.trading_days = 252 #no weekends or holidays
        self.portfolio = None

    def plot_mv(self):
        risk_df = pd.DataFrame(data=np.diag(self.cov),
                            index=self.stock_df.columns,
                            columns=['Volatility'])
        print(risk_df, self.mean)
    


