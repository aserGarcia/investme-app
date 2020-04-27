import pandas as pd 
import scipy.optimize as spo
import numpy as np
import ts_graph_tool
import matplotlib.pyplot as plt

class MVOptimization:

    def __init__(self, stock_df,name):
        '''
        Desc - constructor for mean variance on stocks
        @param: stock_df -  pandas df stock time series
        @param: name - name appended to the output weights file
        '''
        self.name = name

        self.stock_df = stock_df
        self.returns = stock_df.pct_change()
        self.mean_ret = self.returns.mean()
        self.cov_ret = self.returns.cov()
        self.trading_days = 252 #no weekends or holidays
        self.risk_free_rate = 0.75 #04/08/2020
        #equal initial weights
        self.init_weights = np.full(self.mean_ret.shape[0],1.0/self.mean_ret.shape[0])
        self.portfolios = None


    #-----------------------------------------------------#
    #               Objective Functions                   #       
    #-----------------------------------------------------#
    def annualPerformance(self, weights, mean_ret, cov_mat, only_mean=False, only_var=False):
        '''
        Desc - calculates portfolio performance on mean variance
        @param: weights - distributed weghts on portfolio options
        @param: mean_returns - average returns on time series
        @param: cov_mat - covariance matrix on stocks
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

    def sharpeRatio(self, weights, mean_ret, cov_mat,sign = 1.0):
        '''
        Desc - Non-parametric Sharpe Ratio for weights and annual mean returns. 
        @param: weights - portions to invest in
        @param: mean_ret - mean returns pandas dataframe
        @param: cov_mat - covariance matrix
        @param: sign - returns negative sharpe ratio for minimization purposes
        '''
        mean_ret = mean_ret*self.trading_days
        cov_mat = cov_mat*self.trading_days
        return sign*(np.dot(weights.T, mean_ret))/np.sqrt(np.dot(weights.T, np.dot(cov_mat, weights)))

    #-----------------------------------------------------#
    #               Optimization Algorithms               #       
    #-----------------------------------------------------#
    def bestSharpeRatio(self):
        '''
        Desc - Optimizes portfolio weights off Sharpe Ratio
        '''
        #sum of weights is 1
        constraints = ({'type':'eq','fun':lambda x: np.sum(x)-1})

        #no short selling (i.e. weights > 0)
        bounds = tuple((0.0,1.0) for stock in range(self.stock_df.shape[1]))
        
        args = (self.mean_ret, self.cov_ret, -1.0)
        opt_weights = spo.minimize(self.sharpeRatio, self.init_weights, args=args,
                                 method='SLSQP',bounds=bounds, constraints=constraints)
        return opt_weights

    def bestVariance(self):
        '''
        Desc - Optimizes portfolio weights off best Variance
        '''
        #sum of weights is 1
        constraints = ({'type':'eq','fun':lambda x: np.sum(x)-1})

        #no short selling (i.e. weights > 0)
        bounds = tuple((0.0,1.0) for stock in range(self.stock_df.shape[1]))

        #only_mean=False, only_var=True
        args = (self.mean_ret, self.cov_ret, False, True)
        opt_weights = spo.minimize(self.annualPerformance, self.init_weights, args=args,
                                 method='SLSQP',bounds=bounds, constraints=constraints)
        return opt_weights


    def bestEfficiency(self, target_return):
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
    #              Optmizing Portfolio Options            #       
    #-----------------------------------------------------#
    def buildPortfolios(self):
        '''
        Desc - Calculates best portfolio options off Minimum Risk
                and the Sharpe Ratio
        '''
        #Sharpe Ratio 
        shp = self.bestSharpeRatio()
        shp_alloc =  self.annualPerformance(shp['x'],self.mean_ret,self.cov_ret)

        #Best Variance
        min_var = self.bestVariance()
        min_var_alloc = self.annualPerformance(min_var['x'], self.mean_ret, self.cov_ret)

        #Portfolio Options Dataframe
        options_tuple = list(zip(shp_alloc, min_var_alloc))
        options_df = pd.DataFrame(data={'Returns':options_tuple[0], 'Volatility':options_tuple[1]})

        option_weights_df = pd.DataFrame(data={
                                               'Stocks':self.mean_ret.index,
                                               'Sharpe Ratio':shp['x'],
                                               'Minimum Risk':min_var['x']
                                             })
        option_weights_df.to_csv('weights_'+self.name,index=False)

        self.portfolios = options_df.copy()


    #-----------------------------------------------------#
    #                  Plotting Functions                 #       
    #-----------------------------------------------------#
    def plot_pctChange(self):
        '''
        Desc - Interactive plot of the mean returns from initial date
        '''
        ts_graph_tool.ts_slider(self.returns)

    def plot_portfolios(self):
        '''
        Desc - PieCharts on portfolio build
        '''
        if self.portfolios == None:
            self.buildPortfolios()
        portfolio_weights = pd.read_csv("weights_"+self.name)
        ts_graph_tool.plot_pie(portfolio_weights)

    def plot_mv(self,efficient_frontier=True):
        '''
        Desc - plot mean vs. variance. Interactive plotly graph
                Includes Efficient Fontier, Sharpe Ratio, Risk Aversion,
                and Least Variance Portfolio Options
        '''

        #-------------------------------------------#
        #       Annual Volatility/Return Calc       #
        #-------------------------------------------#
        risk_df = pd.DataFrame(data=np.sqrt(np.diag(self.cov_ret)*self.trading_days),
                            index=self.stock_df.columns,
                            columns=['Volatility'])
        
        #getting annualized mean returns for all stocks
        mean_df = self.mean_ret.to_frame(name="Expected_Return")*self.trading_days
        mv_df = pd.concat([risk_df,mean_df],axis=1).reset_index().rename(columns={'index':'Sectors'})

        #------------------------------------------#
        #       Graphing Efficienct Frontier       #
        #------------------------------------------#
        if efficient_frontier:
            
            min_var_w = self.bestVariance()
            ret_min_var, std_min = self.annualPerformance(min_var_w['x'],self.mean_ret,self.cov_ret)
            target_returns = np.linspace(ret_min_var, 0.15, 50)
            pts = np.empty(target_returns.shape[0], dtype=np.float64)
            for i,r in enumerate(target_returns):
                #getting volatility for each target return
                pts[i] = self.bestEfficiency(r)['fun']
            
            efficiency_df = pd.DataFrame(data = {'Target_Return':target_returns, 'Volatility':pts})
            efficiency_df = efficiency_df[efficiency_df.pct_change()['Volatility'].abs()>1e-08]
        
        #portfolio Options, MinRisk, Sharpe Ratio
        if self.portfolios == None:
            self.buildPortfolios()

        #Graphing ALL Points
        ts_graph_tool.plot_meanVariance(mv_df, efficiency_df, self.portfolios)

    

    


