from ts_graph_tool import DashBoard
import pandas as pd

#set during argparse


dash = DashBoard(name="Top Down Investing",)
sector_w = pd.read_csv('../asset_allocation/portfolio_data/weights_sectors.csv')


#Sharpe Ratio Portfolio for MV Optimization and GRU
shp_portfolio = pd.read_csv('../asset_allocation/portfolio_data/sharpe_chosen_stocks.csv')
true_shp = pd.read_csv('../asset_allocation/ml_data/sharpe_true.csv')
pred_shp = pd.read_csv('../asset_allocation/ml_data/sharpe_gru_predicted.csv')
shp_gru_portfolio = pd.read_csv('../asset_allocation/portfolio_data/sharpe_gru_weights.csv')


#Min Risk Portfolio for MV Optimization and GRU
mr_portfolio = pd.read_csv('../asset_allocation/portfolio_data/minrisk_chosen_stocks.csv')
true_mr = pd.read_csv('../asset_allocation/ml_data/minimumRisk_true.csv')
pred_mr = pd.read_csv('../asset_allocation/ml_data/minimumRisk_gru_predicted.csv')
mr_gru_portfolio = pd.read_csv('../asset_allocation/portfolio_data/minimumRisk_gru_weights.csv')


dash.plot_pie(sector_w[['Stocks','Sharpe Ratio']],
              sector_w[['Stocks','Minimum Risk']],
              title='Sector Portions',
              )

#dash.plot_predictions(true_shp, pred_shp, title='True and Predicted Sharpe Ratio Stocks')
dash.plot_pie(shp_portfolio.rename(columns={'Weights':'Sharpe Ratio'}),
              shp_gru_portfolio.rename(columns={'Weights':'Sharpe Ratio'}),
              title='Sharpe Ratio',
              gru=True
            )

#dash.plot_predictions(true_mr, pred_mr,title='True and Predicted Minimum Risk Stocks')
dash.plot_pie(mr_portfolio.rename(columns={'Weights':'Minimum Risk'}),
              mr_gru_portfolio.rename(columns={'Weights':'Minimum Risk'}),
              title='Minimum Risk',
              gru=True
            )

#open local host with dashboard.
dash.create_dashboard()
dash.app.run_server()