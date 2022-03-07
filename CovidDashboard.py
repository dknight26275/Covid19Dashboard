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
covid_cleaned_df = pd.read_csv('H:/Covid19Dashboard/covid_cleaned.csv')
country_daily_df = pd.read_csv('H:/Covid19Dashboard/country_daily.csv')
country_latest_df = pd.read_csv('H:/Covid19Dashboard/country_latest.csv')
daily_total_df = pd.read_csv('H:/Covid19Dashboard/daily_total.csv')

last_update = daily_total_df['Date'].max()  # need to check whether the df needs sorting first

# --------------------------------------------------------------------------------------------------------------
# App Layout
# %%
# app.layout = html.Div(
#     id='root',
#     children=[
#         html.Div(
#             id='banner',
#             children=[
#                 dbc.Row(
#                     dbc.Col(html.H1('COVID19 Pandemic Dashboard', style={'text-align': 'center'}),
#                             width={'size': 8},
#                             id='banner_title'
#                             ),
#                     dbc.Col(html.H4('Last updated on {}'.format(last_update)),
#                             width={'size': 4},
#                             id='banner_last_update'
#                             )
#                 ),
#             ]
#         ),
#         # change this div to hold 2 bar graphs, one for cases, one for deaths
#         # each bar chart should have a button to switch between cumulative and weekly values
#         html.Div(
#             id='global_barchart_container',
#             children=[
#                 dbc.Row(
#                     dbc.Col(
#                         dcc.Dropdown(
#                             id='barchart_dropdown',
#                             options=[
#                                 {'label': 'Total cases', 'value': 'Cumulative cases'},
#                                 {'label': 'New cases', 'value': 'New_cases'},
#                                 {'label': 'Total deaths', 'value': 'Total Deaths'},
#                                 {'label': 'New deaths', 'value': 'New_deaths'}
#                             ],
#                             value='Cumulative cases'
#                         ),
#                         width=4
#                     ),
#                 ),
#                 dbc.Row(dbc.Col(dcc.Graph(id='barchart', figure={}), width=4)), # cases barcharts
#                 dbc.Row(dbc.Col(dcc.Graph(id='barchart', figure={}), width=4)) # deaths barchart
#             ]
#         )
#     ]
# )
#
# '''
# Need to figure out how to fix the dropdown styling on dark backgrounds
# '''
#%%
# demo layout with rows of different heights
# https://github.com/facultyai/dash-bootstrap-components/issues/286
app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.P("This is column 1"),
                    width=8,
                    style={"height": "100%", "background-color": "red"},
                ),
                dbc.Col(
                    html.P("This is column 2"),
                    width=4,
                    style={"height": "100%", "background-color": "green"},
                ),
            ],
            className="h-75",
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.P("This is column 3"),
                    width=8,
                    style={"height": "100%", "background-color": "blue"},
                ),
                dbc.Col(
                    html.P("This is column 4"),
                    width=4,
                    style={"height": "100%", "background-color": "cyan"},
                ),
            ],
            className="h-25",
        ),
    ],
    style={"height": "100vh"},
)



# --------------------------------------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
# %%
# @app.callback(
#     Output(component_id='barchart', component_property='figure'),
#     [Input(component_id='barchart_dropdown', component_property='value')]
# )
# def update_barchart(selected_barchart):
#     print(selected_barchart)
#
#     # sort, filter and group the daily totals df
#     df = daily_total_df.copy()
#     df = df.rename(columns={'Confirmed': 'Cumulative cases', 'Deaths': 'Total Deaths'})
#     # convert date colum to datetime format
#     df['Date'] = pd.to_datetime(df['Date'], infer_datetime_format=True)
#     # sort by Date
#     df = df.sort_values('Date', ignore_index=True)
#     # group data by week
#     df_weekly = df.groupby(by=[pd.Grouper(key='Date', axis=0, freq='W')]) \
#         [['Date', 'Cumulative cases', 'Total Deaths', 'New_cases', 'New_deaths']].agg(
#         {'Cumulative cases': 'max',  # No of confirmed cases at the end of the week
#          'Total Deaths': 'max',  # No of deaths  at the end of the week
#          'New_cases': 'sum',  # number of new cases each day throughout the week
#          'New_deaths': 'sum'}  # number of new deaths each day throughout the week
#     ).reset_index()  # flatten multi-index for px
#
#     bar = px.bar(df_weekly
#                  , x='Date'
#                  , y=selected_barchart
#                  , opacity=0.9
#                  , orientation='v'
#                  , barmode='relative'
#                  , title='Weekly COVID19 {}'.format(selected_barchart)
#                  , hover_data=['Date', selected_barchart]
#                  , template='simple_white'
#                  , labels={'Date': 'Date',
#                            selected_barchart: '{} per week'.format(selected_barchart)})
#
#     bar.update_layout(font={'family': 'arial', 'size': 16}, )
#     bar.update_yaxes(showgrid=False, tickfont={'family': 'arial', 'size': 14})
#     bar.update_xaxes(showgrid=False, tickfont={'family': 'arial', 'size': 14})
#     if (selected_barchart == 'Cumulative cases'):
#         bar.update_traces(marker_color='#115806')
#     elif (selected_barchart == 'New_cases'):
#         bar.update_traces(marker_color='#115806')
#     else:
#         bar.update_traces(marker_color='#A32323')
#
#     return bar
#
#
# '''
# Maybe change bar charts so the New cases appears as a line plot overlaying the cumulative cases, or vice-versa
# '''
# %%
# --------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
