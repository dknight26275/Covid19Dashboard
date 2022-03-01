import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import dash
from dash import html, dcc
from dash.dependencies import Input, Output

app = dash.Dash(__name__)
# --------------------------------------------------------------------------------------------------------------
# Import and clean data
#%%
# (bees example from Charming data)
# df = pd.read_csv('intro_bees.csv')
#
# df = df.groupby(['State', 'ANSI', 'Affected by', 'Year', 'state_code'])[['Pct of Colonies Impacted']].mean()
# df.reset_index(inplace=True)
# print(df.head())
#%%
covid_cleaned_df = pd.read_csv('H:/Covid19Dashboard/covid_cleaned.csv')
country_daily_df = pd.read_csv('H:/Covid19Dashboard/country_daily.csv')
country_latest_df = pd.read_csv('H:/Covid19Dashboard/country_latest.csv')
daily_total_df = pd.read_csv('H:/Covid19Dashboard/daily_total.csv')

# --------------------------------------------------------------------------------------------------------------
# App Layout
#%%
# (bees example from Charming data)
# app.layout = html.Div([
#
#     html.H1('Web Application Dashboards with Dash', style={'text-align': 'center'}),
#
#     dcc.Dropdown(id='slct_year',
#                  options=[
#                      {'label': '2015', 'value': 2015},
#                      {'label': '2016', 'value': 2016},
#                      {'label': '2017', 'value': 2017},
#                      {'label': '2018', 'value': 2018}],
#                  multi=False,
#                  value=2015,
#                  style={'width':'40%'}
#                  ),
#
#     html.Div(id='output_container', children=[]),
#     html.Br(),
#
#     dcc.Graph(id='my_bee_map', figure={})
# ])
#%%
app.layout = html.Div([
    html.H1('COVID19 Pandemic Dashboard', style={'text-align':'center'}),
    dcc.Dropdown(id='barchart_dropdown',
        options=[
            {'label':'Total cases', 'value': 'Cumulative cases'},
            {'label':'New cases', 'value': 'New_cases'},
            {'label': 'Total deaths', 'value': 'Total Deaths'},
            {'label': 'New deaths', 'value': 'New_deaths'}
        ],
        value='Cumulative cases'
    ),
    html.Div(id='output_container', children=[]),
    html.Br(),
    dcc.Graph(id='barchart', figure={})
])


# --------------------------------------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
#%%
# @app.callback(
#     [Output(component_id='output_container', component_property='children'),
#      Output(component_id='my_bee_map', component_property='figure')],
#     [Input(component_id='slct_year', component_property='value')]
# )
# def update_graph(option_slctd):
#     print(option_slctd)
#     print(type(option_slctd))
#
#     container = 'The year chosen by user was: {}'.format(option_slctd)
#
#     dff = df.copy()
#     dff = dff[dff['Year']==option_slctd]
#     dff = dff[dff['Affected by']=='Varroa_mites']
#
#     # #Plotly Express
#     # fig = px.choropleth(
#     #     data_frame=dff,
#     #     locationmode='USA-states',
#     #     locations='state_code',
#     #     scope='usa',
#     #     color='Pct of Colonies Impacted',
#     #     hover_data=['State','Pct of Colonies Impacted'],
#     #     color_continuous_scale=px.colors.sequential.YlOrRd,
#     #     labels={'Pct of Colonies Impacted': '% of Bee Colonies'},
#     #     template='plotly_dark'
#     # )
#
#     # Plotly Graph objects
#     fig = go.Figure(
#         data=[go.Choropleth(
#             locationmode='USA-states',
#             locations=dff['state_code'],
#             z=dff['Pct of Colonies Impacted'].astype(float),
#             colorscale='Reds'
#         )]
#     )
#     fig.update_layout(
#         title_text='Bees Affected by Mites in the USA',
#         title_xanchor='center',
#         title_font=dict(size=24),
#         title_x=0.5,
#         geo=dict(scope='usa')
#     )
#
#
#     return container, fig

#%%
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='barchart', component_property='figure')],
    [Input(component_id='barchart_dropdown',component_property='value')]
)

def update_barchart(selected_barchart):
    print(selected_barchart)

    container = 'Selected Chart: {}'.format(selected_barchart)

    #sort, filter and group the daily totals df
    df = daily_total_df.copy()
    df = df.rename(columns={'Confirmed': 'Cumulative cases', 'Deaths': 'Total Deaths'})
    # convert date colum to datetime format
    df['Date'] = pd.to_datetime(df['Date'], infer_datetime_format=True)
    # sort by Date
    df = df.sort_values('Date', ignore_index=True)
    # group data by week
    df_weekly = df.groupby(by=[pd.Grouper(key='Date', axis=0, freq='W')]) \
        [['Date', 'Cumulative cases', 'Total Deaths', 'New_cases', 'New_deaths']].agg(
        {'Cumulative cases': 'max',  # No of confirmed cases at the end of the week
         'Total Deaths': 'max',  # No of deaths  at the end of the week
         'New_cases': 'sum',  # number of new cases each day throughout the week
         'New_deaths': 'sum'}  # number of new deaths each day throughout the week
         ).reset_index()  # flatten multi-index for px

    bar = px.bar(df_weekly
                 , x='Date'
                 , y=selected_barchart
                 , opacity=0.9
                 , orientation='v'
                 , barmode='relative'
                 , title='Weekly COVID19 {}'.format(selected_barchart)
                 , hover_data=['Date', selected_barchart]
                 , template='seaborn'
                 ,labels={'Date':'Date',
                      selected_barchart:'Weekly COVID19 {}'.format(selected_barchart)})

    bar.update_layout(font={'family': 'arial', 'size': 16}, )
    bar.update_yaxes(showgrid=False, tickfont={'family': 'arial', 'size': 14})
    bar.update_xaxes(showgrid=False, tickfont={'family': 'arial', 'size': 14})
    if (selected_barchart == 'Cumulative cases'):
        bar.update_traces(marker_color='#115806')
    elif (selected_barchart == 'New_cases'):
        bar.update_traces(marker_color='#115806')
    else:
        bar.update_traces(marker_color='#A32323')

    return container, bar

'''
Probably need to resize it, once I get other graphs added
'''
# --------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)