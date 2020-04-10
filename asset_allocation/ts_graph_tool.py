
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


def plot_meanVariance(df, eff_df):
    '''
    Desc - Interactive plot for mean variance analysis
    @param df - dataframe with expected returns and volatility
    @param eff_df - efficiency dataframe for the efficiency fronteir
    '''
    print(list(df.Sectors))

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
                            x=0.9,y=1.1
                        )
                        
            )

    fig = go.Figure(layout=layout)

    fig.add_trace(
        go.Scatter(x=df.Volatility,
                   y=df.Expected_Return,
                   mode='markers+text',
                   name='Sectors',
                   text=[sector.replace("_avg","").replace("_"," ") for sector in df.Sectors],
                   textposition="bottom right",
                   marker=dict(
                       size=list(df.Volatility*150),
                       color=list(df.Volatility),
                       colorscale='Aggrnyl',
                       colorbar=dict(
                                    title="Volatility"
                                )
                   )
                )
    )
    
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

    fig.show()