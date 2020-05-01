
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

import dash
import dash_core_components as dcc
import dash_html_components as html

font_dict = dict(
                family="Courier New, monospace",
                size = 18,
                color = "#7f7f7f"
                )

class DashBoard:

    def __init__(self,name):
        #figures will be added to the list to be iterated through and
        #displayed later
        self.figures=[]
        self.css_list = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
        self.app = dash.Dash(name=name,external_stylesheets=self.css_list)

    def create_dashboard(self):
        #stacking the figures in the front end (no HTML, CSS, of Javascript! Wohoo!)
        self.app.layout = html.Div([
            dcc.Graph(figure=set_figure) for set_figure in self.figures    
        ])

    def ts_slider(self,df):
        '''
        Desc - Interactive time series with sliders to zoom in/out.
                plotly will open a local host page for the interactive plot.
        @param: df - data frame with date as index, stocks as columns
        '''

        #create figure
        fig = go.Figure()
        for stock in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=list(df[stock]),name=stock)
            )

        #setting title
        fig.update_layout(title_text="Sector Averages with Sliders")
        
        # Add range slider
        fig.update_layout(
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                            label="1m",
                            step="month",
                            stepmode="backward"),
                        dict(count=6,
                            label="6m",
                            step="month",
                            stepmode="backward"),
                        dict(count=1,
                            label="YTD",
                            step="year",
                            stepmode="todate"),
                        dict(count=1,
                            label="1y",
                            step="year",
                            stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(
                    visible=True
                ),
                type="date"
            ),
            font=font_dict
        )
        
        fig.show()

    def plot_ml(self,loss, val_loss):
        #plotting function for machine learning training
        epochs = [i for i in range(len(loss))]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=epochs, y=loss, name="Training Loss"))
        fig.add_trace(go.Scatter(x=epochs, y=val_loss, name="Validation Loss"))
        fig.update_layout(title_text="Training and Validation Loss vs. Epochs",
                        font=font_dict)
        self.figures.append(fig)

    def plot_predictions(self,true_df, pred_df,title):
        #plotting predictions of machine leraning and true prices
        true_df = true_df.truncate(after=10)
        pred_df = pred_df.truncate(after=10)

        fig = go.Figure()
        for stock in true_df.columns:
            fig.add_trace(
                go.Scatter(x=true_df.index, y=list(true_df[stock]),name=stock)
            )
            fig.add_trace(
                go.Scatter(x=pred_df.index, y=list(pred_df[stock]),name="Predicted "+stock)
            )
        fig.update_layout(title_text = title,
                        font = font_dict)
        self.figures.append(fig)

    def plot_pie(self,df1,df2,title,gru=False):
        '''
        Desc - Interactive Pie Chart of portfolios built
        @param: portfolio_df - dataframe with stock column, weights per portfolio
                allocation method
        '''
        #getting number of methods without the stock labels
        from math import ceil
        rows_num = 1
        cols = (1,2)
        if gru:
            add_title = ' GRU'
        else: add_title = ''
        
        fig = make_subplots(rows=rows_num, cols=len(cols),
                            specs=[[{'type':'domain'}]*len(cols)]*rows_num,
                            subplot_titles=[df1.columns[1],df2.columns[1]+add_title]
                            )
        
        

        fig.add_trace(
            go.Pie(
                name=df1.columns[1],
                labels=df1.Stocks,
                values=df1.iloc[:,1],
                ),
            row=1,
            col=1
        )

        
        fig.add_trace(
            go.Pie(
                name=df2.columns[1],
                labels=df2.Stocks,
                values=df2.iloc[:,1],
                marker=dict(
                    colors=px.colors.sequential.deep[::-1]
                )
                ),
            row=1,
            col=2
        )
                
        
        fig.update_traces(hole=0.4,hoverinfo="label+percent+name",textposition='inside')


        fig.update_layout(
            title_text = title,
            font=font_dict,
        )

        for i in fig['layout']['annotations']:
            i['font'] = dict(size=20)

        self.figures.append(fig)

    def plot_meanVariance(self,df, eff_df, options_df):
        '''
        Desc - Interactive plot for mean variance analysis
        @param: df - dataframe with expected returns and volatility
        @param: eff_df - efficiency dataframe for the efficiency fronteir
        @param: shp_alloc - portfolio return and std tuple of best sharpe ratio
        '''

        layout = go.Layout(
                    title="Annual Sector Expected Returns vs. Volatility",
                    font=font_dict,
                    xaxis=dict(
                        title="Volatility"
                    ),
                    yaxis=dict(
                        title="Annual Returns"
                    ),
                    legend=dict(
                        x=0.9,y=1.13
                    )
                            
                )

        fig = go.Figure(layout=layout)

        #-----------------------------------------------------#
        #            Plotting Efficiency Frontier             #       
        #-----------------------------------------------------#

        fig.add_trace(
            go.Scatter(
                x=eff_df.Volatility,
                y=eff_df.Target_Return,
                mode='lines',
                name='Efficient Frontier',
                line=dict(
                    width=4,
                    color='#505a74',
                    shape='spline'
                )
            )
        )


        #-----------------------------------------------------#
        #                  Plotting Stock Scatter             #       
        #-----------------------------------------------------#

        size_scale=150

        fig.add_trace(
            go.Scatter(
                x=df.Volatility,
                y=df.Expected_Return,
                mode='markers+text',
                name='Sectors',
                text=[sector.replace("_avg","").replace("_"," ") for sector in df.Sectors],
                textposition="bottom right",
                marker=dict(
                    size=list(df.Volatility*size_scale),
                    color=list(df.Volatility),
                    colorscale='Aggrnyl',
                    colorbar=dict(
                                title="Volatility"
                            ),
                    line=dict(color='DarkSlateGrey')
                )
            )
        )
        #-----------------------------------------------------#
        #            Plotting Portfolio Options               #       
        #-----------------------------------------------------#

        fig.add_trace(
            go.Scatter(
                x=options_df.Volatility,
                y=options_df.Returns,
                name="Portfolio Options",
                mode='markers+text',
                text=["Sharpe-Ratio",
                    "Least-Variance"],
                textposition="top center",
                textfont=dict(
                    color="#37474f"
                ),
                showlegend=True,
                marker=dict(
                    size=list(options_df.Volatility*size_scale),
                    color=list(options_df.Volatility),
                    colorscale="magenta",
                    line=dict(color='DarkSlateGrey'),
                    opacity=0.9
                )
            )

        )

        self.figures.append(fig)