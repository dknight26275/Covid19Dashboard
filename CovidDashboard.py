import pandas as pd
from datetime import datetime

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
from dash.dash_table.Format import Format, Scheme
from dash.dash_table import DataTable, FormatTemplate
import dash_bootstrap_components as dbc


app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.CYBORG],
                # meta_tags=[
                #     {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
                # ],
                )
# other dash themes : https://bootswatch.com/

# --------------------------------------------------------------------------------------------------------------
# %%
# load data
# covid_cleaned_df = pd.read_csv('H:/Covid19Dashboard/covid_cleaned.csv')
# country_daily_df = pd.read_csv('H:/Covid19Dashboard/country_daily.csv')
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


country_bar_df = country_latest_df.copy()
# set datatable number formating
# numeric = Format().group(True)
# percentage = FormatTemplate.percentage(2)
# numeric_decimal = Format(group=Group.yes).groups([3, 2])

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
conf = '#4B9D3E' # colour for styling confirmed cases

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
                        dbc.ListGroupItem(
                            "Confirmed cases in the last month: {:,} ({:+.2f}%)".format(
                                cases_last_month,cases_one_month_change_pc)),
                        dbc.ListGroupItem(
                            "COVID 19 deaths in the last month: {:,} ({:+.2f}%)".format(
                                deaths_last_month,deaths_one_month_change_pc)),
                        dbc.ListGroupItem(
                            "Confirmed cases in the last week: {:,} ({:+.2f}%)".format(
                                cases_last_week, cases_one_week_change_pc)),
                        dbc.ListGroupItem(
                            "COVID 19 deaths in the last week: {:,} ({:+.2f}%)".format(
                                deaths_last_week,deaths_one_week_change_pc)),
                    ],
                    className='card-text'
            )
        ]
    ),
    ],
    className='card text-white bg-secondary mb-3'
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
                                [html.H5('Data sourced from JHU CSSE', style={'text-align': 'center',
                                                                              'color':'white',
                                                                              'font-style':'italic'})],
                                href="https://github.com/CSSEGISandData/COVID-19",
                                className='nav-item'
                            ),
                            width=2,
                            style={"height": "100%"},
                            className='nav-link'
                        ),
                        dbc.Col(
                            html.H1('COVID19 Pandemic Dashboard', style={'text-align': 'center',
                                                                         'color':'white',
                                                                         'font-weight':'bold'}),
                            width=8,
                            style={"height": "50%"},
                            # className='nav-link active'
                        ),
                            dbc.Col(
                            [html.H4('Last updated: ', style={'text-align': 'center',
                                                              'color':'white',
                                                              'font-weight':'bold'}),
                            html.P('{}'.format(last_update), style={'text-align': 'center',
                                                                    'color':'white'},)],
                            width=2,
                            style={"height": "100%",},
                        )
                    ],
                    className=['h-100', 'w-100',]
                ),
            ],
            style={'height': '10%',},
            className='navbar navbar-expand-lg navbar-dark bg-primary'
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
                                    inputClassName='form-check-input',
                                    labelStyle={
                                        'padding':'10px'
                                    }
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
                                    inputClassName='form-check-input',
                                    labelStyle={
                                        'padding':'10px'
                                    }
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
                            # className='card text-white bg-secondary mb-3'
                        )
                    ]


                ),
                dbc.Row(
                    children=[
                        dbc.Col(
                            id='datatable_container',
                            children=[
                                dash_table.DataTable(
                                    id='interactive_datable',
                                    columns=[
                                        dict(name='Country',id='Country_Region', selectable=True, deletable=False, type='text',),
                                        dict(name='Confirmed cases',id='Confirmed', selectable=True,
                                             deletable=False, type='numeric',format=Format().group(True)),
                                        dict(name='Deaths', id='Deaths', selectable=True,
                                             deletable=False, type='numeric', format=Format().group(True)),
                                        dict(name='Fatality rate',id='Deaths_per_100', selectable=True,
                                             deletable=False, type='numeric',format=FormatTemplate.percentage(2)),
                                        dict(name='Cases/1 million population', id='Cases_per_million', selectable=True,
                                             deletable=False, type='numeric', format=Format(precision=2, scheme=Scheme.fixed)),
                                        dict(name='28 day cases', id='New_cases_last_month', selectable=True,
                                             deletable=False, type='numeric', format=Format().group(True)),
                                        dict(name='28 day deaths', id='New_deaths_last_month', selectable=True,
                                             deletable=False, type='numeric', format=Format().group(True)),
                                    ],
                                    data=country_bar_df.to_dict('records'),
                                    editable=False,
                                    filter_action='native',
                                    sort_action='native',
                                    sort_mode='single',
                                    column_selectable='single',
                                    row_selectable='multi',
                                    row_deletable=False,
                                    selected_columns=[],
                                    selected_rows=[],
                                    page_action='native',
                                    page_current=0,
                                    page_size=10,
                                    # style_data={
                                    #     'whiteSpace': 'normal', 'height': 'auto'
                                    # },
                                    style_cell_conditional=[
                                        {
                                            'if': {'column_id': 'Country_Region'},
                                            'textAlign': 'left'
                                        },
                                    ],
                                    style_header={
                                        'backgroundColor':'rgb(42,159,214)',
                                        'color':'#fff'
                                    },
                                    style_cell={
                                        'minWidth': 175,
                                        # 'maxWidth':200, 'width':95
                                    },
                                    style_data={
                                        'backgroundColor': '#adafae',
                                        'color':'black',
                                    },
                                    style_data_conditional=[
                                        {
                                            'if': {'row_index': 4},
                                            'backgroundColor': 'rgb(220, 220, 220)',
                                        }
                                    ],
                                ),

                            ],
                            width=10,
                            # style={'background-color':'grey'},
                            className='table table-hover'
                        ),

                    ]
                ),
                dbc.Row(
                    children=[
                        dbc.Col(
                            id='map_container',
                            children=[
                                dcc.Graph(id='choropleth_map', figure={}),
                            ],
                            width={'size': 12},
                            style={'height': '100%', },
                        ),
                        # dbc.Col(
                        #     id='Selected_data_container',
                        #     children=[
                        #         dcc.Graph(id='datatable_graph', figure={})
                        #     ],
                        #     width=4,
                        # )
                    ]

                ),

            ],

        ),
    ],
    id='root',
    style={'max-width':'100vw', 'max-height':'100vh'}
)


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
                            , template='plotly_dark'
                            , labels={'Date': 'Date',
                           selected_barchart: 'Covid19 cases'})

    cases_barchart.update_layout({'font': {'family': 'arial', 'size': 12},
                                  'plot_bgcolor':'rgba(0,0,0,0)',
                                  'paper_bgcolor':'rgba(0,0,0,0)'
                                  }
                                 )
    cases_barchart.update_yaxes(showgrid=False, tickfont={'family': 'arial', 'size': 12},linecolor='white')
    cases_barchart.update_xaxes(showgrid=False, tickfont={'family': 'arial', 'size': 12},linecolor='white')
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
                             , template='plotly_dark'
                             , labels={'Date': 'Date',
                           selected_barchart: 'Deaths'})

    deaths_barchart.update_layout({'font': {'family': 'arial', 'size': 12},
                                  'plot_bgcolor':'rgba(0,0,0,0)',
                                  'paper_bgcolor':'rgba(0,0,0,0)'
                                  }
                                 )
    deaths_barchart.update_yaxes(showgrid=False, tickfont={'family': 'arial', 'size': 12},linecolor='white')
    deaths_barchart.update_xaxes(showgrid=False, tickfont={'family': 'arial', 'size': 12},linecolor='white')
    deaths_barchart.update_traces(marker_color=dths,marker_line_color='rgba(0,0,0,0)', marker_line_width=0.05)


    return deaths_barchart


@app.callback(
    Output(component_id='choropleth_map',component_property='figure'),
    [Input(component_id='interactive_datable', component_property='derived_virtual_data'),
     Input(component_id='interactive_datable',component_property='derived_virtual_selected_rows'),
     Input(component_id='interactive_datable',component_property='selected_columns')],
)
def update_selected_barchart(all_rows_data,slctd_rows_indices,selected_columns):
    print('Data across all pages pre or post filtering: {}'.format(all_rows_data))
    print('---------------------')
    print('Indices of selected rows if part of table after filtering: {}'.format(slctd_rows_indices))


    dff = pd.DataFrame(all_rows_data)

    borders= [5 if i in slctd_rows_indices else 1 for i in range(len(dff))]
    if len(selected_columns)==0:
        selected_column='Confirmed'
    else:
        selected_column=selected_columns[0]
    figure = px.choropleth(
            data_frame=dff,
            locations='Country_Region',
            locationmode='country names',
            color=selected_column,
            color_continuous_scale='jet',
            template='plotly_dark',
            hover_data=['Country_Region', 'Confirmed','Deaths']
        )
    figure.update_traces(marker_line_width=borders)
    figure.update_layout({'font': {'family': 'arial', 'size': 12},
                                  'plot_bgcolor':'rgba(0,0,0,0)',
                                  'paper_bgcolor':'rgba(0,0,0,0)'
                                  }
                                 )
    return figure

'''
need to work on styling of graphs...
'''

@app.callback(
    Output('interactive_datable','style_data_conditional'),
    [Input('interactive_datable','selected_columns')]
)

def update_table_styles(selected_columns):
    print('Selected columns: {}'.format(selected_columns))

    return [
        {
            'if': {'column_id':i},
            'background_color':'#D2F3FF'
        }
        for i in selected_columns
    ]
#%%
# --------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
