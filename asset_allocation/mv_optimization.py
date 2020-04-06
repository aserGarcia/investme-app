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
        self.cov = stock_df.cov()
        self.mean = stock_df.mean(axis=0)
        self.returns = stock_df.pct_change()
        self.m_returns = self.returns.mean(axis=0)
        self.cov_ret = self.returns.cov()
        self.trading_days = 252 #no weekends or holidays
        #equal initial weights
        self.init_weights = np.full(stock_df.shape[1],1.0/stock_df.shape[1])
        self.portfolio = None


    #------------Objective Functions------------------#

    def pfPerformance(self, weights, mean_returns, cov_mat, only_mean=False, only_var=False):
        '''
        Desc - calculates portfolio performance on mean variance
        @param weights - distributed weghts on portfolio options
        @param mean_returns - average returns on time series
        @param cov_mat - covariance matrix on stocks
        '''
        ret = np.dot(weights.T,mean_returns)*self.trading_days
        risk = np.sqrt(np.dot(weights.T, np.dot(cov_mat,weights))*self.trading_days)
        return_value = None
        if only_mean:
            return_value = ret
        elif only_var:
            return_value = risk
        else:
            return_value = (ret, risk)
        return return_value

    def riskAversion(self, weights, alpha, mean_returns, cov_mat, sign=-1.0):
        return np.dot(weights.T, mean_returns)-alpha*np.dot(weights.T,np.dot(cov_mat, weights))

    def sharpeRatio(self, weights, mean_returns, cov_mat):
        return np.dot(weights.T, mean_returns)/np.sqrt(np.dot(weights.T,np.dot(cov_mat, weights)))

    #------------Optimization Algorithms----------------#
    
    def optRiskAversion(self, alpha=0.5):
        #sum of weights is 1
        constraints = ({'type':'eq','fun':lambda x: np.sum(x)-1})

        #no short selling (i.e. weights > 0)
        bounds = tuple((0.0,1.0) for stock in range(self.stock_df.shape[1]))
        #args for risk aversion
        args = (alpha, self.m_returns, self.cov_ret)
        opt_weights = spo.minimize(self.riskAversion, self.init_weights, args=args,
                                 method='SLSQP',bounds=bounds, constraints=constraints)
        return opt_weights

    def optSharpeRatio(self):
        #sum of weights is 1
        constraints = ({'type':'eq','fun':lambda x: np.sum(x)-1})

        #no short selling (i.e. weights > 0)
        bounds = tuple((0.0,1.0) for stock in range(self.stock_df.shape[1]))
        #args for risk aversion
        args = (self.m_returns, self.cov_ret)
        opt_weights = spo.minimize(self.sharpeRatio, self.init_weights, args=args,
                                 method='SLSQP',bounds=bounds, constraints=constraints)
        return opt_weights

    def optVariance(self):
        #sum of weights is 1
        constraints = ({'type':'eq','fun':lambda x: np.sum(x)-1})

        #no short selling (i.e. weights > 0)
        bounds = tuple((0.0,1.0) for stock in range(self.stock_df.shape[1]))
        #args for risk aversion

        #only_mean=False, only_var=True
        args = (self.m_returns, self.cov_ret, False, True)
        opt_weights = spo.minimize(self.pfPerformance, self.init_weights, args=args,
                                 method='SLSQP',bounds=bounds, constraints=constraints)
        return opt_weights


    def optEfficiency(self, target_return):
        #sum of weights is 1 and expected return is close to target

        def pfReturn(weights):
            return self.pfPerformance(weights, self.m_returns, self.cov_ret, only_mean=True)

        constraints = ({'type':'eq','fun':lambda x: np.sum(x)-1},
                        {'type':'eq','fun':lambda x: pfReturn(x)-target_return})

        #no short selling (i.e. weights > 0)
        bounds = tuple((0.0,1.0) for stock in range(self.stock_df.shape[1]))
        #args for risk aversion
        #only_mean=False, only_var=True
        args = (self.m_returns, self.cov_ret, False, True)
        opt_weights = spo.minimize(self.pfPerformance, self.init_weights, args=args,
                                 method='SLSQP',bounds=bounds, constraints=constraints)
        return opt_weights


    #---------------Plotting Functions-----------------#

    def plot_pctChange(self):
        '''
        Desc - Interactive plot of the mean returns from initial date
        '''
        ts_graph_tool.ts_slider(self.returns)


    def plot_mv(self,efficient_frontier=True):
        '''
        Desc - plot mean vs. variance. Interactive plotly graph
        '''
        risk_df = pd.DataFrame(data=np.diag(self.cov_ret),
                            index=self.stock_df.columns,
                            columns=['Volatility'])
        #self.mean = self.m_returns.mean(axis=0)
        mean_df = self.m_returns.to_frame(name="Expected_Return")
        mv_df = pd.concat([risk_df,mean_df],axis=1).reset_index().rename(columns={'index':'Sectors'})


        #TODO: Graph efficiency frontier
        if efficient_frontier:
            min_var_w = self.optVariance()
            ret_min, std_min = self.pfPerformance(min_var_w['x'],self.m_returns,self.cov_ret)
            
            target_returns = np.linspace(ret_min, 0.3, 50)
            pts =[]
            for idx,r in enumerate(target_returns):
                pts.append(self.optEfficiency(r)['fun'])
            print(pts)

        #Calculating coefficient of variance
        CV = risk_df.Volatility/mean_df.Expected_Return
        ts_graph_tool.plot_meanVariance(mv_df, CV)
        

    


