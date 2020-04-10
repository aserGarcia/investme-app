
import plotly.graph_objects as go


font_dict = dict(
                family="Courier New, monospace",
                size = 18,
                color = "#7f7f7f"
                )

def ts_slider(df):
    '''
    Desc - Interactive time series with sliders to zoom in/out.
            plotly will open a local host page for the interactive plot.
    @param df - data frame with date as index, stocks as columns
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


def plot_meanVariance(df, eff_df, options_df):
    '''
    Desc - Interactive plot for mean variance analysis
    @param df - dataframe with expected returns and volatility
    @param eff_df - efficiency dataframe for the efficiency fronteir
    @param shp_alloc - portfolio return and std tuple of best sharpe ratio
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
        go.Scatter(x=eff_df.Volatility,
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
        go.Scatter(x=df.Volatility,
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

    fig.show()