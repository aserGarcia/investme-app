import pandas as pd 
import scipy as scp
import numpy as np
import ts_graph_tool

class MVOptimization:

    def __init__(self, stock_df):
        '''
        Desc - constructor for mean variance on stocks
        @param stock_df -  pandas df stock time series
        '''
        self.stock_df = stock_df
        self.cov = stock_df.cov()
        self.mean = stock_df.mean(axis=0)
        self.trading_days = 252 #no weekends or holidays
        self.weights = np.zeros(stock_df.shape[1])
        self.portfolio = None

    

    def plot_mv(self):
        '''
        Desc - plot mean vs. variance. Interactive plotly graph
        '''
        risk_df = pd.DataFrame(data=np.diag(self.cov),
                            index=self.stock_df.columns,
                            columns=['Volatility'])
        mean_df = self.mean.to_frame(name="Expected_Return")
        mv_df = pd.concat([risk_df,mean_df],axis=1).reset_index().rename(columns={'index':'Sectors'})

        #Calculating coefficient of variance
        CV = risk_df.Volatility/mean_df.Expected_Return
        ts_graph_tool.plot_meanVariance(mv_df, CV)
        #TODO: Plot efficient frontier from solving Markowitz model
    


