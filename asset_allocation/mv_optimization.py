import pandas as pd 
import scipy as scp
import seaborn as sns
import numpy as np

class MVOptimization:

    def __init__(self, stock_list=None):
    '''
    Desc - constructor for mean variance on stocks
    @param stocks - time series of stocks/sectors to analyze pandas dataframe
    '''
        # M stocks for T time window timeseries
        # Must contain 'Symbol' and 'Sector'
        if stock_list == None:
            print("WARNING: No stocks provided, run method \"setStocks\" to optimize portfolio.")
        self.stock_list = stock_list
        self.cov = None
        # Store stock {"stock_name": [mean_return, risk (sd)]}
        self.stock_stats = {} 
        self.trading_days = 252 #no weekends or holidays
        self.portfolio = None

    def setRandomStocks(self, portfolio_size=18, alpha=0.5):
        '''
        Desc - sets stocks to later distribute investment into. First is random,
                secnd method is 
        @param random - choose stocks at random, else choose stocks by low risk aversion
        @param n_stocks - size of portfolio
        @param alpha - risk parameter to take on portfolio
        '''
        #choose stocks at random
        try:
            n_stock_options = self.stock_list.count()['Symbol']
        except Exception as e:
            if str(e) == "KeyError":
                print("\"Symbol\" needs to be the column name of the stock symbols")
            else: 
                print("ERROR: ", str(e))
            return 0
        indexes = np.random.randint(0,n_stock_options, size=portfolio_size)
        self.stock_list = self.stock_list.iloc[indexes]
        print("STOCKS CHOSEN: ", self.stock_list['Symbol'])
       
    def setMinRiskSectorStocks(self, portfolio_size=18, alpha=0.5):
        try:
            # dictionary of sector: stock id index from stock_list (*not symbol)
            sectors_dict = self.stock_list.groupby(['Sector']).groups
            
        except KeyError:
            print("ERROR: stock list needs column \"Sector\")
        

    def setStockStats(self, stock_timeseries):
        '''
        Desc - sets the input stock stats to the class vars
            @param stock_timeserie
        '''
        try:
            self.cov = stock_timeseries.cov()
            #TODO set stock stats, *after choosing stocks (keeps cov mat smaller)
        except Exception as e:
            print("ERROR: Could not set stat: %s,\nEnsure stock data is a dataframe",str(e))

    def performance(self, weights, mean_returns, cov_mat, time_window):
        '''
        Desc - performance on stock pool for specified time window
        Returns std (standard deviation e.g. Risk), returns (total returns for the year)
        Ex. by Ricky Kim - 2018
        @param - weights: portions of portfolio given to each stock
        @param mean_returns: vector of means from simple returns over times series per stock
        @param cov_mat: matrix of stock covariance matrix
        '''
        portfolio_returns = np.sum(weights*mean_returns)*time_window
        volatility = np.sqrt(np.dot(weights, np.dot(cov_mat, weights))*time_window)
        return volatility, portfolio_returns

    #TODO:
    #   Solve matrix for weights
    #   Graph stocks for returns
    #   Get year that the portfolio is for
    def visualizePortfolio(self,mean_returns, risk_fr, cov_mat):
        '''
        Desc - visualize portfolio allocation
        @param mean_returns: vector of means from simple returns over times series per stock
        @param risk_fr: risk free return, what the returns are with zero risk
        @param cov_mat: matrix of stock covariance matrix
        '''
        print("-"*100)
        print("Maximum Sharpe Ratio Portfolio: ")
        print("Year: ", year)
        print("Annual Return: ", )
        print("Annual Volatility: ", )
        print("-"*100)


