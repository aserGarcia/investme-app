
import plotly.graph_objects as go
import plotly.express as px

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


def plot_meanVariance(df, CV):
    '''
    Desc - Interactive plot for mean variance analysis
    @param df - dataframe with expected returns and volatility
    '''

    fig = px.scatter(df, x="Volatility",y="Expected_Return",
                    size=CV,color="Sectors", hover_name="Sectors",
                    color_discrete_sequence=px.colors.qualitative.Vivid)

    fig.update_layout(
                        title="Sector Expected Returns vs. Volatility",
                        font=font_dict
                        )

    fig.show()