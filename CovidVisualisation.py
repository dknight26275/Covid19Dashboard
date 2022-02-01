# imports/Initialization
# import dash
# from dash import dash_table
# import dash_core_components as dcc
# import dash_html_components as html
# from dash.dependencies import State, Input, Output

import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.io as pio
from plotly.subplots import make_subplots
import plotly as py
# py.offline.init_notebook_mode(connected=True)

import folium

import pandas as pd
import numpy as np
from datetime import datetime
# import matplotlib.pylot as plt

import math
import random
from datetime import timedelta
import os

dths = '#A32323' # colour for styling deaths
conf = '#115806' # colur for styling confirmed cases

# %%
# load cleaned/processed data
covid_cleaned_df = pd.read_csv('H:/Covid19Dashboard/covid_cleaned.csv')
country_daily_df = pd.read_csv('H:/Covid19Dashboard/country_daily.csv')
country_latest_df = pd.read_csv('H:/Covid19Dashboard/country_latest.csv')
daily_total_df = pd.read_csv('H:/Covid19Dashboard/daily_total.csv')

print(f'covid_cleaned: {covid_cleaned_df.info()}')
print(f'country_daily{country_daily_df.info()}')
print(f'country_latest: {country_latest_df.info()}')
print(f'daily_total: {daily_total_df.info()}')

#%%
# Maps cases and deaths (total, last week, last month, per 100000 population)

#%%
'''Bar graphs
weekly global cases/deaths (Cumulative and new cases/deaths) (use daily_total)
continent/Country breakdown - same graphs, maybe line plots?
racing bar graph of top 10 (20?) nations, cases/deaths'''
#%%
''' Create df for Barplots of Global total confirmed cases and deaths'''
# create copy of daily_totals
global_barplots_df = daily_total_df.copy()
#rename columns for better display
global_barplots_df = global_barplots_df.rename(columns={'Confirmed':'Cumulative cases',
                                                        'Deaths':'Total Deaths',
                                                        'Deaths_per_100':'Deaths/100 cases',
                                                        'No_countries': 'Number of Countries'})
# convert date colum to datetime format
global_barplots_df['Date'] = pd.to_datetime(global_barplots_df['Date'], infer_datetime_format=True)
# sort by Date
global_barplots_df = global_barplots_df.sort_values('Date', ignore_index=True)

# group data by week
global_barplots_weekly_df = global_barplots_df.groupby(by=[pd.Grouper(key='Date', axis=0, freq='W')]) \
    [['Date','Cumulative cases','Total Deaths','New_cases','New_deaths','Deaths/100 cases','Number of Countries']].agg(
    {'Cumulative cases':'max', # No of confirmed cases at the end of the week
     'Total Deaths':'max', # No of deaths  at the end of the week
     'New_cases':'sum', # number of new cases each day throughout the week
     'New_deaths':'sum', # number of new deaths each day throughout the week
     'Deaths/100 cases':'mean', # mean number of deaths per 100000 each day throughout the week
     'Number of Countries':'max'}  # No of countries with reported cases
).reset_index() # flatten multi-index for px

#%%
''' Create df for Barplots of confirmed cases and deaths grouped by continent/country'''

#%%
# function to style bar plots
def barplot(df,x,y,hoverdata=[],title=None,xlabel=None,ylabel=None,color=None):
    bar = px.bar(df
             , x=x
             , y=y
             , opacity=0.9
             , orientation='v'
             , barmode='relative'
             , title=title
             , hover_data=hoverdata
             , template='seaborn'
             ,labels={x:xlabel,
                      y:ylabel})

    bar.update_layout(font={'family':'arial', 'size':16}, )
    bar.update_traces(marker_color=color)
    bar.update_yaxes(showgrid=False, tickfont={'family':'arial', 'size':14})
    bar.update_xaxes(showgrid=False, tickfont={'family':'arial', 'size':14})
    return bar
    # bar.show()
print('function created')
#%%
weekly_Cumulativecases_plot = barplot(df=global_barplots_weekly_df,
                                      x='Date',
                                      y='Cumulative cases',
                                      hoverdata=['New_cases','Number of Countries'],
                                      title='Global Cumulative Covid-19 cases',
                                      xlabel='Date',
                                      ylabel='Total Covid-19 cases',
                                      color=conf)
weekly_Newcases_plot = barplot(df=global_barplots_weekly_df,
                               x='Date',
                               y='New_cases',
                               hoverdata=['Cumulative cases', 'Number of Countries'],
                               title='Global Daily Covid-19 cases',
                               xlabel='Date',
                               ylabel='Weekly cases',
                               color=conf)
weekly_Cumulativedeaths_plot = barplot(df=global_barplots_weekly_df,
                                      x='Date',
                                      y='Total Deaths',
                                      hoverdata=['New_deaths','Deaths/100 cases'],
                                      title='Global Covid-19 Deaths',
                                      xlabel='Date',
                                      ylabel='Total Covid-19 Deaths',
                                      color=dths)
weekly_Newdeaths_plot = barplot(df=global_barplots_weekly_df,
                                      x='Date',
                                      y='New_deaths',
                                      hoverdata=['Total Deaths','Deaths/100 cases'],
                                      title='Global Weekly Covid-19 Deaths',
                                      xlabel='Date',
                                      ylabel='Weekly Covid-19 Deaths',
                                      color=dths)
weekly_Cumulativecases_plot.show()
#%%
'''Racing Bar chart - display horizontal bar charts of top 10(?) countries (one for confirmed cases, one for deaths
Animate the bar chart with each frame displaying data from one month, starting Jan 2020'''
# use country_daily as base for racing bar chart df
racing_bar_df = country_daily_df.copy()
# convert Date column to datetype for grouping
# racing_bar_df['Date'] = pd.to_datetime(racing_bar_df['Date'],infer_datetime_format=True)
# group by country and Month, only need continent, confirmed and deaths column
racing_bar_df = racing_bar_df.groupby(by=['Date','Country_Region', ])[['Country_Region',   # pd.Grouper(key='Date', axis=0, freq='M')
'Continent', 'Confirmed','Deaths']].agg({'Continent':'first',
                                        'Confirmed':'max',
                                        'Deaths':'max'}).reset_index()

# calculate max values to set range for X-axis
conf_upper_range = (racing_bar_df['Confirmed'].max())*1.1
dths_upper_range = (racing_bar_df['Deaths'].max())*1.1
# create dictionary to hold data for animation, each key-value pair will be data for one frame of the animated bar chart

# create list of unique dates  - each frame of the animation will be based on data from a single month
dates =[]
for date in racing_bar_df['Date'].unique():
    dates.append(date)

# create list for dictionary keys
dict_keys = []
for i in range(len(dates)):
    dict_keys.append('frame'+str(i+1))

# create dictionary for confirmed cases
confirmed_dict = {}
for date,key in zip(dates, dict_keys):
    df = racing_bar_df[racing_bar_df['Date']==date] # get all data for selected month
    df = df.nlargest(20,columns=['Confirmed'])
    df = df.sort_values(by=['Date','Confirmed'])
    confirmed_dict[key] = df[['Date','Country_Region','Continent','Confirmed']]
#%%

racing_bar = go.Figure(
    data = [
        go.Bar(
            x=confirmed_dict['frame1']['Confirmed'],
            y=confirmed_dict['frame1']['Country_Region'],
            orientation='h',
            text=confirmed_dict['frame1'][['Country_Region','Confirmed']],
            textfont={'family':'arial','size':18},
            textposition='inside',
            insidetextanchor='middle',
            width=0.9
        )
    ],
    layout=go.Layout(
        xaxis={'range':[0, conf_upper_range], 'autorange':False, 'title':{'text':'Covid-19 cases', 'font':{'size': 18}}},
        yaxis={'range':[-0.5, 20.5], 'autorange':False, 'tickfont':{'size': 14}},
        title={'text':'Covid_19 cases by Country', 'font':{'size':28}, 'x': 0.5, 'xanchor': 'center'},
        # Add button
        updatemenus=[{
            'type':"buttons",
            'buttons':[{'label': "Play",
                        'method': "animate",
                        # https://github.com/plotly/plotly.js/blob/master/src/plots/animation_attributes.js
                        'args': [None,
                                 {"frame": {"duration": 100, "redraw": True},
                                  "transition": {"duration": 25,
                                                 "easing": "linear"}}
                                 ]
                        }]
            }]
    ),
    frames=[
        go.Frame(
            data=[
                go.Bar(x=value['Confirmed'], y=value['Country_Region'],
                       orientation='h', text=value['Confirmed'])
            ],
            layout=go.Layout(
                xaxis={'range': [0, (confirmed_dict[key]['Confirmed'].max())*1.1], 'autorange': False},
                yaxis={'range':[-0.5, 20.5], 'autorange':False, 'tickfont':{'size':14}},
                title={'text':'Covid-19 cases by Country: ' + str(value['Date'].values[0]),'font': {'size': 28}}
            )
        )
        for key, value in confirmed_dict.items()
    ]
)
pio.show(racing_bar)

'''
Need to look at animation speed (slow down a little,
look at the y axis layout, make it larger enough in the first frame to fit all labels (should prevent jittering in early frames)
Add a colour scheme so different countries are different colours...
'''

#%%
