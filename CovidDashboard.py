import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SANDSTONE])
# other dash themes : https://bootswatch.com/

# --------------------------------------------------------------------------------------------------------------
# %%
# load data
covid_cleaned_df = pd.read_csv('H:/Covid19Dashboard/covid_cleaned.csv')
country_daily_df = pd.read_csv('H:/Covid19Dashboard/country_daily.csv')
country_latest_df = pd.read_csv('H:/Covid19Dashboard/country_latest.csv')
daily_total_df = pd.read_csv('H:/Covid19Dashboard/daily_total.csv')

# sort, filter and group the daily totals bar_df
bar_df = daily_total_df.copy()
bar_df = bar_df.rename(columns={'Confirmed': 'Cumulative cases', 'Deaths': 'Total Deaths'})
# convert date colum to datetime format
bar_df['Date'] = pd.to_datetime(bar_df['Date'], infer_datetime_format=True)
# sort by Date
bar_df = bar_df.sort_values('Date', ignore_index=True)
# group data by week
df_weekly = bar_df.groupby(by=[pd.Grouper(key='Date', axis=0, freq='W')]) \
    [['Date', 'Cumulative cases', 'Total Deaths', 'New_cases', 'New_deaths']].agg(
    {'Cumulative cases': 'max',  # No of confirmed cases at the end of the week
     'Total Deaths': 'max',  # No of deaths  at the end of the week
     'New_cases': 'sum',  # number of new cases each day throughout the week
     'New_deaths': 'sum'}  # number of new deaths each day throughout the week
).reset_index()  # flatten multi-index for px


# initialise variables
last_update = daily_total_df['Date'].max()
global_total_cases = int(country_latest_df['Confirmed'].sum())
global_total_deaths = int(country_latest_df['Deaths'].sum())
cases_per_million = int(country_latest_df['Cases_per_million'].mean())
deaths_per_100 = country_latest_df['Deaths_per_100'].mean()
cases_last_month = int(country_latest_df['New_cases_last_month'].sum())
cases_one_month_change_pc = (cases_last_month/global_total_cases)*100
deaths_last_month = int(country_latest_df['New_deaths_last_month'].sum())
deaths_one_month_change_pc = (deaths_last_month/global_total_deaths)*100
cases_last_week = int(country_latest_df['New_cases_last_week'].sum())
cases_one_week_change_pc = (cases_last_week/global_total_cases)*100
deaths_last_week = int(country_latest_df['New_deaths_last_week'].sum())
deaths_one_week_change_pc = (deaths_last_week/global_total_deaths)*100

dths = '#A32323' # colour for styling deaths
conf = '#115806' # colur for styling confirmed cases

# --------------------------------------------------------------------------------------------------------------
# App Layout

# %%
# demo layout with rows of different heights
# https://github.com/facultyai/dash-bootstrap-components/issues/286
app.layout = dbc.Container(
    id='root',
    children=[
        html.Div(
            id='banner',
            children=[
                dbc.Row(
                    [
                        dbc.Col(
                            html.A(
                                [html.H5('Data sourced from JHU CSSE', style={'text-align': 'center'})],
                                href="https://github.com/CSSEGISandData/COVID-19"
                            ),
                            width=2,
                            style={"height": "100%"},
                        ),
                        dbc.Col(
                            html.H1('COVID19 Pandemic Dashboard', style={'text-align': 'center'}),
                            width=8,
                            style={"height": "100%"},
                        ),
                            dbc.Col(
                            html.H4('Last updated: {}'.format(last_update), style={'text-align': 'center'}),
                            width=2,
                            style={"height": "100%"},
                        )
                    ],
                    className='h-100'
                ),
            ],
            style={'height': '10%'}
        ),
        html.Div(
            id='container',
            children=[
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Row(  # white bg
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Row(
                                                    id='country_select',
                                                    children=[
                                                         dcc.Dropdown(
                                                            id='country_dropdown',
                                                            options=[{'label':x,'value':x} for x in country_latest_df.Country_Region.unique()],
                                                            placeholder='Select a country'
                                                        ),
                                                    ],
                                                    style={'height': '50%',}
                                                ),
                                                dbc.Row(
                                                    id='country_charts',
                                                    children=[
                                                        html.H5('Selected Country charts'),
                                                        dcc.Graph(id='selected_country_barcharts', figure={}),
                                                    ],
                                                    style={'height': '50%',},
                                                )
                                            ],
                                            width={'size': 3},
                                            style={'height': '100%',},
                                        ),
                                        dbc.Col(
                                            id='map_container',
                                            children=[
                                                html.H5('Choropleth map'),
                                                dcc.Graph(id='choropleth_map', figure={}),
                                            ],
                                            width={'size': 6},
                                            style={'height': '100%',},
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Row(
                                                    id='global_cases',
                                                    children=[
                                                        html.H5('Global cases barchart'),
                                                        dcc.RadioItems(
                                                            id='global_cases_selector',
                                                            options=
                                                            [
                                                                {'label':'Cumulative', 'value':'Cumulative cases'},
                                                                {'label':'Weekly', 'value':'New_cases'}
                                                            ],
                                                            value='New_cases',
                                                            # inline=True
                                                        ),
                                                        dcc.Graph(id='global_cases_barchart', figure={}),
                                                    ],
                                                    style={'height': '50%',}
                                                ),
                                                dbc.Row(
                                                    id='global_deaths',
                                                    children=[
                                                        html.H5('Global deaths barchart'),
                                                        dcc.RadioItems(
                                                            id='global_deaths_selector',
                                                            options=
                                                            [
                                                                {'label': 'Cumulative', 'value': 'Total Deaths'},
                                                                {'label': 'Weekly', 'value': 'New_deaths'}
                                                            ],
                                                            value='New_deaths',
                                                            # inline=True
                                                        ),
                                                        dcc.Graph(id='global_deaths_barchart', figure={}),
                                                    ],
                                                    # width={'size':6},
                                                    style={'height': '50%',},
                                                )
                                            ],
                                            # style={'height':'100%'},
                                            width={'size': 3},
                                            style={"height": "100%",},
                                        ),
                                    ],
                                    style={'height': '66%',}
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            id='selected_country_stats',
                                            children=[ #maybe make this a table?
                                                html.H5("Selected country stats"),
                                                html.H6("Total COVID 19 cases:  ###"),
                                                html.H6("Total COVID 19 related deaths: ###?"),
                                                html.H6("COVID 19 cases in the last month:  ###"),
                                                html.H6("COVID 19 related deaths in the last month: ###?"),
                                                html.H6("COVID 19 cases in the last week:  ###"),
                                                html.H6("COVID 19 related deaths in the last week: ###?"),
                                            ],
                                            width=3,
                                            style={"height": "100%",},
                                        ),
                                        dbc.Col(
                                            id='global_cumulative_stats',
                                            children=[
                                                html.H5("Total cases and deaths globally"),
                                                html.H6("Total COVID 19 cases:  {}".format(global_total_cases)),
                                                html.H6("Total COVID 19 related deaths: {}".format(global_total_deaths)),
                                                html.H6("COVID 19 related cases per million people: {}".format(cases_per_million)),
                                                html.H6("COVID 19 related deaths/100 cases: {}".format(deaths_per_100)),
                                            ],
                                            width=3,
                                            style={"height": "100%",},
                                        ),
                                        dbc.Col(
                                            id='global_28days_stats',
                                            children=[
                                                html.H5("Global cases and deaths in last 28 days"),
                                                html.H6("COVID 19 cases in the last month: {}".format(cases_last_month)),
                                                html.H6("Percentage change from the previous month: {}".format(cases_one_month_change_pc)),
                                                html.H6("Total COVID 19 related deaths in the last month: {}".format(deaths_last_month)),
                                                html.H6("Percentage change from the previous month: {}".format(deaths_one_month_change_pc)),

                                            ],
                                            width=3,
                                            style={"height": "100%",},
                                        ),
                                        dbc.Col(
                                            id='global_7days_stats',
                                            children=[
                                                html.H5("Global cases and deaths in last 7 days"),
                                                html.H6("COVID 19 cases in the last week: {}".format(cases_last_week)),
                                                html.H6("Percentage change from the previous week: {}".format(cases_one_week_change_pc)),
                                                html.H6("Total COVID 19 related deaths in the last week: {}".format(deaths_last_week)),
                                                html.H6("Percentage change from the previous week: {}".format(deaths_one_week_change_pc)),
                                            ],
                                            width=3,
                                            style={"height": "100%",},
                                        ),
                                    ],
                                    style={'height': '34%',}
                                ),
                            ]
                        )
                    ],
                    style={'height': '90%',}
                ),
            ],
            style={'height': '100%'}
        )
    ],
    style={"height": "100vh"},
)
'''
Maybe use cards for the country and global stats..., either that or some css to style the bottom columns
'''
# --------------------------------------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
# %%
#global cases barcharts
@app.callback(
    Output(component_id='global_cases_barchart', component_property='figure'),
    [Input(component_id='global_cases_selector', component_property='value')]
)
def update_cases_barchart(selected_barchart):
    print(selected_barchart)

    cases_barchart = px.bar(df_weekly
                 , x='Date'
                 , y=selected_barchart
                 , opacity=0.9
                 , orientation='v'
                 , barmode='relative'
                 # , title='Global COVID19 {}'.format(selected_barchart)
                 , hover_data=['Date', selected_barchart]
                 , template='simple_white'
                 , labels={'Date': 'Date',
                           selected_barchart: '{} per week'.format(selected_barchart)})

    cases_barchart.update_layout(font={'family': 'arial', 'size': 12}, )
    cases_barchart.update_yaxes(showgrid=False, tickfont={'family': 'arial', 'size': 12})
    cases_barchart.update_xaxes(showgrid=False, tickfont={'family': 'arial', 'size': 12})
    cases_barchart.update_traces(marker_color=conf)

    return cases_barchart

#global deaths barcharts
@app.callback(
    Output(component_id='global_deaths_barchart', component_property='figure'),
    [Input(component_id='global_deaths_selector', component_property='value')]
)
def update_deaths_barchart(selected_barchart):
    print(selected_barchart)

    deaths_barchart = px.bar(df_weekly
                             , x='Date'
                             , y=selected_barchart
                             , opacity=0.9
                             , orientation='v'
                             , barmode='relative'
                             # , title='Global COVID19 {}'.format(selected_barchart)
                             , hover_data=['Date', selected_barchart]
                             , template='simple_white'
                             , labels={'Date': 'Date',
                           selected_barchart: '{} per week'.format(selected_barchart)})

    deaths_barchart.update_layout(font={'family': 'arial', 'size': 12}, )
    deaths_barchart.update_yaxes(showgrid=False, tickfont={'family': 'arial', 'size': 12})
    deaths_barchart.update_xaxes(showgrid=False, tickfont={'family': 'arial', 'size': 12})
    deaths_barchart.update_traces(marker_color=dths)

    return deaths_barchart



# --------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
