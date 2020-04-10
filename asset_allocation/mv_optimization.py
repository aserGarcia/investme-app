import pandas as pd 
import scipy.optimize as spo
import numpy as np
import ts_graph_tool
import matplotlib.pyplot as plt

class MVOptimization:

    def __init__(self, stock_df):
        '''
        Desc - constructor for mean variance on stocks
        @param stock_df -  pandas df stock time series
        '''
        self.stock_df = stock_df
        self.returns = stock_df.pct_change()
        self.mean_ret = self.returns.mean()
        self.cov_ret = self.returns.cov()
        self.trading_days = 252 #no weekends or holidays
        self.risk_free_rate = 0.75 #04/08/2020
        #equal initial weights
        self.init_weights = np.full(self.mean_ret.shape[0],1.0/self.mean_ret.shape[0])


    #-----------------------------------------------------#
    #               Objective Functions                   #       
    #-----------------------------------------------------#
    def annualPerformance(self, weights, mean_ret, cov_mat, only_mean=False, only_var=False):
        '''
        Desc - calculates portfolio performance on mean variance
        @param weights - distributed weghts on portfolio options
        @param mean_returns - average returns on time series
        @param cov_mat - covariance matrix on stocks
        '''
        ret = np.dot(weights.T,mean_ret)*self.trading_days
        risk = np.sqrt(np.dot(weights.T, np.dot(cov_mat,weights)))*np.sqrt(self.trading_days)
        return_value = None
        if only_mean:
            return_value = ret
        elif only_var:
            return_value = risk
        else:
            return_value = (ret, risk)
        return return_value

    def riskAversion(self, weights, alpha, mean_ret, cov_mat, sign=-1.0):
        return sign*np.dot(weights.T, mean_ret)-alpha*np.dot(weights.T,np.dot(cov_mat, weights))

    def sharpeRatio(self, weights, mean_ret, cov_mat,sign = 1.0):
        '''
        Desc - Sharpe Ratio for weights and mean returns
        @param weights - portions to invest in
        @param mean_ret - mean returns pandas dataframe
        @param cov_mat - covariance matrix
        @param sign - returns negative sharpe ratio for minimization purposes
        '''
        rt, std = self.annualPerformance(weights, mean_ret, cov_mat)
        return sign*(rt-self.risk_free_rate)/std

    #-----------------------------------------------------#
    #               Optimization Algorithms               #       
    #-----------------------------------------------------#
    def optRiskAversion(self, alpha=0.5):
        #sum of weights is 1
        constraints = ({'type':'eq','fun':lambda x: np.sum(x)-1})

        #no short selling (i.e. weights > 0)
        bounds = tuple((0.0,1.0) for stock in range(self.stock_df.shape[1]))
        
        args = (alpha, self.mean_ret, self.cov_ret)
        opt_weights = spo.minimize(self.riskAversion, self.init_weights, args=args,
                                 method='SLSQP',bounds=bounds, constraints=constraints)
        return opt_weights

    def optSharpeRatio(self):
        #sum of weights is 1
        constraints = ({'type':'eq','fun':lambda x: np.sum(x)-1})

        #no short selling (i.e. weights > 0)
        bounds = tuple((0.0,1.0) for stock in range(self.stock_df.shape[1]))
        
        args = (self.mean_ret, self.cov_ret, -1.0)
        opt_weights = spo.minimize(self.sharpeRatio, self.init_weights, args=args,
                                 method='SLSQP',bounds=bounds, constraints=constraints)
        return opt_weights

    def optVariance(self):
        #sum of weights is 1
        constraints = ({'type':'eq','fun':lambda x: np.sum(x)-1})

        #no short selling (i.e. weights > 0)
        bounds = tuple((0.0,1.0) for stock in range(self.stock_df.shape[1]))

        #only_mean=False, only_var=True
        args = (self.mean_ret, self.cov_ret, False, True)
        opt_weights = spo.minimize(self.annualPerformance, self.init_weights, args=args,
                                 method='SLSQP',bounds=bounds, constraints=constraints)
        return opt_weights


    def optEfficiency(self, target_return):
        #sum of weights is 1 and expected return is close to target

        def annualReturn(weights):
            return self.annualPerformance(weights, self.mean_ret, self.cov_ret, only_mean=True)

        constraints = ({'type':'eq','fun':lambda x: np.sum(x)-1},
                        {'type':'eq','fun':lambda x: target_return-annualReturn(x)})

        #no short selling (i.e. weights > 0)
        bounds = tuple((0.0,1.0) for stock in range(self.stock_df.shape[1]))
        
        #args at end only_mean=False, only_var=True
        args = (self.mean_ret, self.cov_ret, False, True)
        opt_weights = spo.minimize(self.annualPerformance, self.init_weights, args=args,
                                 method='SLSQP',bounds=bounds, constraints=constraints)
        return opt_weights


    #-----------------------------------------------------#
    #                  Plotting Functions                 #       
    #-----------------------------------------------------#
    def plot_pctChange(self):
        '''
        Desc - Interactive plot of the mean returns from initial date
        '''
        ts_graph_tool.ts_slider(self.returns)


    def plot_mv(self,efficient_frontier=True):
        '''
        Desc - plot mean vs. variance. Interactive plotly graph
        '''
        #getting annualized volatility for all stocks 
        risk_df = pd.DataFrame(data=np.sqrt(np.diag(self.cov_ret)*self.trading_days),
                            index=self.stock_df.columns,
                            columns=['Volatility'])
        
        #getting annualized mean returns for all stocks
        mean_df = self.mean_ret.to_frame(name="Expected_Return")*self.trading_days
        mv_df = pd.concat([risk_df,mean_df],axis=1).reset_index().rename(columns={'index':'Sectors'})

        #TODO: Graph efficiency frontier
        if efficient_frontier:
            shp = self.optSharpeRatio()
            ret_shp, std_shp = self.annualPerformance(shp['x'],self.mean_ret,self.cov_ret)
            min_var_w = self.optVariance()
            ret_min_var, std_min = self.annualPerformance(min_var_w['x'],self.mean_ret,self.cov_ret)
            target_returns = np.linspace(ret_min_var, 0.15, 50)
            pts = np.empty(target_returns.shape[0], dtype=np.float64)
            for i,r in enumerate(target_returns):
                #getting volatility
                pts[i] = self.optEfficiency(r)['fun']
            
            efficiency_df = pd.DataFrame(data = {'Target_Return':target_returns, 'Volatility':pts})
            efficiency_df = efficiency_df[efficiency_df.pct_change()['Volatility'].abs()>1e-08]
        #Calculating coefficient of variance
        ts_graph_tool.plot_meanVariance(mv_df, efficiency_df)

    


