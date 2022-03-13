import pandas as pd
from datetime import datetime

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc


app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.SANDSTONE],
                # meta_tags=[
                #     {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
                # ],
                )
# other dash themes : https://bootswatch.com/

# --------------------------------------------------------------------------------------------------------------
# %%
# load data
covid_cleaned_df = pd.read_csv('H:/Covid19Dashboard/covid_cleaned.csv')
country_daily_df = pd.read_csv('H:/Covid19Dashboard/country_daily.csv')
country_latest_df = pd.read_csv('H:/Covid19Dashboard/country_latest.csv')
daily_total_df = pd.read_csv('H:/Covid19Dashboard/daily_total.csv')

# sort, filter and group the daily_total_df for global bar charts
global_bar_df = daily_total_df.copy()
global_bar_df = global_bar_df.rename(columns={'Confirmed': 'Cumulative cases', 'Deaths': 'Total Deaths'})
# convert date colum to datetime format
global_bar_df['Date'] = pd.to_datetime(global_bar_df['Date'], infer_datetime_format=True)
# sort by Date
global_bar_df = global_bar_df.sort_values('Date', ignore_index=True)
# group data by week
global_df_weekly = global_bar_df.groupby(by=[pd.Grouper(key='Date', axis=0, freq='W')]) \
    [['Date', 'Cumulative cases', 'Total Deaths', 'New_cases', 'New_deaths']].agg(
    {'Cumulative cases': 'max',  # No of confirmed cases at the end of the week
     'Total Deaths': 'max',  # No of deaths  at the end of the week
     'New_cases': 'sum',  # number of new cases each day throughout the week
     'New_deaths': 'sum'}  # number of new deaths each day throughout the week
).reset_index()  # flatten multi-index for px


# sort, filter and group the country_daily_df for selected country bar charts and choropleth chart
country_bar_df = country_daily_df.copy()
country_bar_df = country_bar_df.rename(columns={'Confirmed': 'Cumulative cases', 'Deaths': 'Total Deaths'})
# convert date colum to datetime format
country_bar_df['Date'] = pd.to_datetime(country_bar_df['Date'], infer_datetime_format=True)
# sort by Date
country_bar_df = country_bar_df.sort_values('Date', ignore_index=True)
# group data by week
country_df_weekly = country_bar_df.groupby(by=[pd.Grouper(key='Date', axis=0, freq='W'),'Country_Region']) \
    [['Date', 'Country_Region','Cumulative cases', 'Total Deaths', 'New_cases', 'New_deaths', 'iso3','Lat','Long']].agg(
    {'Cumulative cases': 'max',  # No of confirmed cases at the end of the week
     'Total Deaths': 'max',  # No of deaths  at the end of the week
     'New_cases': 'sum',  # number of new cases each day throughout the week
     'New_deaths': 'sum',  # number of new deaths each day throughout the week
     'iso3': 'last',  # iso3 for choropleth maps
     'Lat': 'last',  # Lat for maps
     'Long': 'last',  # Long for maps
     }
).reset_index()  # flatten multi-index for px


# initialise variables
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

# convert latest date in df to 'Month day year' format
dateparts = daily_total_df['Date'].iloc[-1].split('-')
last_update = datetime(int(dateparts[0]),int(dateparts[1]),int(dateparts[2]))
last_update = last_update.strftime('%B %d %Y')

dths = '#A32323' # colour for styling deaths
conf = '#115806' # colour for styling confirmed cases

#Data Card
global_data_card = dbc.Card(
    children=[
        dbc.CardHeader("Total COVID19 cases and deaths globally"),
        dbc.CardBody(
            children=[
                dbc.ListGroup(
                    children=[
                        dbc.ListGroupItem("Total confirmed cases:  {:,}".format(global_total_cases)),
                        dbc.ListGroupItem("Total COVID 19 related deaths: {:,}".format(global_total_deaths)),
                        dbc.ListGroupItem("COVID 19 cases per million people: {:,}".format(cases_per_million)),
                        dbc.ListGroupItem("COVID 19 deaths/100 cases: {:.2f}".format(deaths_per_100)),
                        dbc.ListGroupItem("Confirmed cases in the last month: {:,} ({:+.2f}%)".format(cases_last_month,cases_one_month_change_pc)),
                        dbc.ListGroupItem("COVID 19 deaths in the last month: {:,} ({:+.2f}%)".format(deaths_last_month,deaths_one_month_change_pc)),
                        dbc.ListGroupItem("Confirmed cases in the last week: {:,} ({:+.2f}%)".format(cases_last_week, cases_one_week_change_pc)),
                        dbc.ListGroupItem("COVID 19 deaths in the last week: {:,} ({:+.2f}%)".format(deaths_last_week,deaths_one_week_change_pc)),
                    ]
            )
        ]
    ),
    ]
)

# --------------------------------------------------------------------------------------------------------------
# App Layout
#%%
app.layout = dbc.Container(
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
                            [html.H4('Last updated: ', style={'text-align': 'center'}),
                            html.P('{}'.format(last_update), style={'text-align': 'center'})],
                            width=2,
                            style={"height": "100%",},
                        )
                    ],
                    className=['h-100', 'w-100',]
                ),
            ],
            style={'height': '10%',}
        ),
        html.Div(
            id='data-container',
            children=[
                dbc.Row(
                    children=[
                        dbc.Col(
                            id='confirmed_chart_container',
                            children=[
                                # html.H5('Global cases barchart'),
                                dcc.RadioItems(
                                    id='weekly_vs_cumulative_cases_selector',
                                    options=
                                    [
                                        {'label': ' Cumulative ', 'value': 'Cumulative cases'},
                                        {'label': ' Weekly ', 'value': 'New_cases'}
                                    ],
                                    value='New_cases',
                                ),
                                dcc.Graph(id='confirmed_cases_barchart', figure={}),
                            ],
                            width=4,
                            # style={'height': '50%',}
                        ),
                        dbc.Col(
                            id='deaths_chart_container',
                            children=[
                                # html.H5('Global cases barchart'),
                                dcc.RadioItems(
                                    id='weekly_vs_cumulative_deaths_selector',
                                    options=
                                    [
                                        {'label': ' Cumulative ', 'value': 'Total Deaths'},
                                        {'label': ' Weekly ', 'value': 'New_deaths'}
                                    ],
                                    value='New_deaths',
                                ),
                                dcc.Graph(id='deaths_barchart', figure={}),
                            ],
                            width=4,
                            # style={'height': '50%',}
                        ),
                        dbc.Col(
                            id='summary_stats_container',
                            children=[
                                global_data_card,
                            ],
                            width=4,
                        )
                    ]


                ),
                dbc.Row(
                    children=[
                        dbc.Col(
                            id='data_table',
                            children=[
                                dash_table.DataTable()
                            ],
                            width=6,
                            style={'background-color':'grey'}
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
                    ]
                )
            ],

        ),
    ],
    id='root',
    style={'max-width':'100vw', 'max-height':'100vh'}
)

#%%
# %%
# demo layout with rows of different heights
# https://github.com/facultyai/dash-bootstrap-components/issues/286
# app.layout = dbc.Container(
#     id='root',
#     children=[
#         html.Div(
#             id='container',
#             children=[
#                 dbc.Row(
#                     [
#                         dbc.Col(
#                             [
#                                 dbc.Row(  # white bg
#                                     [
#                                         dbc.Col(
#                                             [
#                                                 dbc.Row(
#                                                     id='country_select',
#                                                     children=[
#                                                          dcc.Dropdown(
#                                                             id='country_dropdown',
#                                                             options=[{'label':x,'value':x} for x in country_latest_df.Country_Region.unique()],
#                                                             placeholder='Select a country'
#                                                         ),
#                                                         dcc.Dropdown(
#                                                             id='graph-selector',
#                                                             options=[
#                                                                 {'label': 'Cumulative cases', 'value':'Cumulative cases'},
#                                                                 {'label': 'Weekly cases', 'value':'New_cases'},
#                                                                 {'label': 'Cumulative deaths', 'value':'Total Deaths'},
#                                                                 {'label': 'Weekly deaths', 'value':'New_deaths'}
#                                                             ],
#                                                             placeholder='Select a graph'
#                                                         ),
#                                                     ],
#                                                     style={'height': '50%',}
#                                                 ),
#                                                 dbc.Row(
#                                                     id='country_charts',
#                                                     children=[
#                                                         html.H5('Selected Country charts'),
#
#                                                         dcc.Graph(id='selected_country_barcharts', figure={}),
#                                                     ],
#                                                     style={'height': '50%',},
#                                                 )
#                                             ],
#                                             width={'size': 3},
#                                             style={'height': '100%',},
#                                         ),


#                                     ],
#                                     style={'height': '66%',}
#                                 ),
#                                 dbc.Row(
#                                     [
#                                         dbc.Col(
#                                             id='selected_country_stats',
#                                             children=[ #maybe make this a table?
#                                                 html.H5("Selected country stats"),
#                                                 dash_table.DataTable(
#                                                     data=[
#                                                         {'name': '', 'id': 'Values'},
#                                                         {'name':'Total COVID19 cases','id':5555555},
#                                                         {'name':'Total COVID19 deaths','id':4444444},
#                                                         {'name':'COVID19 cases last month','id':333333333},
#                                                         {'name': 'COVID19 deaths last month', 'id': 222222222},
#                                                         {'name': 'COVID19 cases last week', 'id': 111111111},
#                                                         {'name': 'COVID19 deaths last week', 'id': 00000000},
#                                                     ],
#                                                     id='Data_table',
#                                                 )
#                                                 # html.H6("Total COVID 19 cases:  ###"),
#                                                 # html.H6("Total COVID 19 related deaths: ###?"),
#                                                 # html.H6("COVID 19 cases in the last month:  ###"),
#                                                 # html.H6("COVID 19 related deaths in the last month: ###?"),
#                                                 # html.H6("COVID 19 cases in the last week:  ###"),
#                                                 # html.H6("COVID 19 related deaths in the last week: ###?"),
#                                             ],
#                                             width=3,
#                                             style={"height": "100%",},
#                                         ),



#                                     ],
#                                     style={'height': '34%',}
#                                 ),
#                             ]
#                         )
#                     ],
#                     style={'height': '90%',}
#                 ),
#             ],
#             style={'height': '100vh', 'width': '95vw', 'background-color':'green'}
#         )
#     ],
#     style={"height": "100vh", 'width':'100vw'},
# )
# '''
# Maybe use cards for the country and global stats..., either that or some css to style the bottom columns
# '''
# --------------------------------------------------------------------------------------------------------------


#%%
#
# # Connect the Plotly graphs with Dash Components
#
# #confirmed cases barcharts
@app.callback(
    Output(component_id='confirmed_cases_barchart', component_property='figure'),
    [Input(component_id='weekly_vs_cumulative_cases_selector', component_property='value')]
)
def update_cases_barchart(selected_barchart):
    print(selected_barchart)

    cases_barchart = px.bar(global_df_weekly
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

#deaths barcharts
@app.callback(
    Output(component_id='deaths_barchart', component_property='figure'),
    [Input(component_id='weekly_vs_cumulative_deaths_selector', component_property='value')]
)
def update_deaths_barchart(selected_barchart):
    print(selected_barchart)

    deaths_barchart = px.bar(global_df_weekly
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

# # selected country barchart
# @app.callback(
#     Output(component_id='selected_country_barcharts',component_property='figure'),
#     [Input(component_id='country_dropdown', component_property='value'),
#      Input(component_id='graph-selector',component_property='value')],
# )
# def update_selected_barchart(country,graph):
#     print(country, graph)
#
#     dff_weekly = country_df_weekly[country_df_weekly['Country_Region'] == country]
#
#     selected_barchart = px.bar(dff_weekly
#                                , x='Date'
#                                , y=graph
#                                , opacity=0.9
#                                , orientation='v'
#                                , barmode='relative'
#                                # , title='Global COVID19 {}'.format(selected_barchart)
#                                , hover_data=['Date', graph]
#                                , template='simple_white'
#                                , labels={'Date': 'Date',
#                            graph: '{} per week'.format(graph)})
#
#     selected_barchart.update_layout(font={'family': 'arial', 'size': 12}, )
#     selected_barchart.update_yaxes(showgrid=False, tickfont={'family': 'arial', 'size': 12})
#     selected_barchart.update_xaxes(showgrid=False, tickfont={'family': 'arial', 'size': 12})
#     if (graph == 'Cumulative cases') | (graph == 'New_cases'):
#         selected_barchart.update_traces(marker_color=conf)
#     else:
#         selected_barchart.update_traces(marker_color=dths)
#
#     # total_cases = dff_weekly['Cumulative cases'].iloc[-1]
#     # total_deaths = dff_weekly['Total Deaths'].iloc[-1]
#     # cases_in_last_week = dff_weekly['Cumulative cases'].max() - dff_weekly['Cumulative cases'].iloc[-2]
#     # deaths_in_last_week = dff_weekly['Total Deaths'].max() - dff_weekly['Total Deaths'].iloc[-2]
#     # cases_in_last_month = dff_weekly['Cumulative cases'].max() - dff_weekly['Cumulative cases'].iloc[-4]
#     # deaths_in_last_month = dff_weekly['Total Deaths'].max() - dff_weekly['Total Deaths'].iloc[-4]
#
#     return selected_barchart

# @app.callback(
#     Output(component_id='choropleth_map', component_property='figure')
# )
#%%
# --------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
