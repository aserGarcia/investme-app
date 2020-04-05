
import plotly.graph_objects as go

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
        )
    )
    
    fig.show()