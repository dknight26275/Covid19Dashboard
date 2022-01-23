

# imports/Initialization
# import dash
# from dash import dash_table
# import dash_core_components as dcc
# import dash_html_components as html
# from dash.dependencies import State, Input, Output

import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
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


#%%
# load cleaned/processed data
covid_cleaned_df = pd.read_csv('H:/Covid19Dashboard/covid_cleaned.csv', parse_dates=['Date'])
country_daily_df = pd.read_csv('H:/Covid19Dashboard/country_daily.csv', parse_dates=['Date'])
country_latest_df = pd.read_csv('H:/Covid19Dashboard/country_latest.csv')
daily_total_df = pd.read_csv('H:/Covid19Dashboard/daily_total.csv', parse_dates=['Date'])

print(f'covid_cleaned: {covid_cleaned_df.info()}')
print(f'country_daily{country_daily_df.info()}')
print(f'country_latest: {country_latest_df.info()}')
print(f'daily_toal: {daily_total_df.info()}')

#%%
'''Worldwide total confirmed cases and deaths'''
# Remove null values from Province_State column of covid_cleaned_df
covid_cleaned_df['Province_State'] = covid_cleaned_df['Province_State'].fillna('')
