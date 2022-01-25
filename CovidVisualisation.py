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
# import matplotlib.pylot as plt

import math
import random
from datetime import timedelta
import os

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

# %%
'''Worldwide total confirmed cases and deaths'''
# Remove null values from Province_State column of covid_cleaned_df
covid_cleaned_df['Province_State'] = covid_cleaned_df['Province_State'].fillna('')
df = covid_cleaned_df[covid_cleaned_df['Country_Region'] == 'Australia']
bar = px.bar(df, x='Date'  # try settin   to Province_State for animation
             , y='Confirmed'
             , color='Provin ce_State'
             , opacity=0.9
             , orientation=
             'v'
             , barmode='relative'
             , title='Confirmed Covid-19 cases in Australia'
             , template='plotly_dark'
             # ,animation_frame='Date', # need to sort the Date column properly for this to work
             # ,range_y=[0,750000]
             )

bar.show()

'''



Also look at Racing bargraph animation, could look cool
(Not necessary for function, but maybe also look into prettify or something similar for pycharm
'''

#%%


df = pd.read_csv('H:/Covid19Dashboard/daily_total.csv')
# can convert str date cols to datetime
df['Date'] = pd.to_datetime(df['Date'], infer_datetime_format=True)
# group by week
df = df.groupby(pd.Grouper(key='Date', axis=0, freq='W'))['Confirmed','Deaths','New_cases','Deaths_per_100'].agg(
    {'Confirmed':'max','Deaths':'max','New_cases':'sum','Deaths_per_100':'mean'})
print(df.head(10))

#%%
