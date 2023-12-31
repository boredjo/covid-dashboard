from dash import Dash, dcc, html, Input, Output, callback
import os
import pandas as pd
import numpy as np
import plotly.graph_objs as go


from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from datetime import datetime as dt

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output 


cases = pd.read_csv('/data/cases.csv')
selected_date_columns = [col for col in cases.columns if '2020-01-22' <= col <= '2023-07-23']
cases = cases[selected_date_columns]

deaths = pd.read_csv('/data/deaths.csv')
selected_date_columns = [col for col in deaths.columns if '2020-01-22' <= col <= '2023-07-23']
deaths = deaths[selected_date_columns]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div([

    # COVID Cases Interactive
    html.H1("Interactive Dashboard for COVID-19 Cases",
        style={'text-align': 'center'}),

    dcc.DatePickerRange(
        id='cases-date-picker-range',
        start_date='2020-01-22',
        end_date='2023-07-23',
        display_format='YYYY-MM-DD',
        min_date_allowed='2020-01-22',
        max_date_allowed='2023-07-23',
    ),
    
    dcc.RadioItems(
        id='cases-y-axis-scale',
        options=[
            {'label': 'Linear Scale', 'value': 'linear'},
            {'label': 'Log Scale', 'value': 'log'},
        ],
        value='linear',
        labelStyle={
            'display': 'block',
            'font-size': '20px'
        },
    ),
    
    dcc.Graph(id='cases-graph', style={
        'border-style': 'solid',
        'border-width': '5px'
    }),


    # COVID Deaths Interactive
    html.H1("Interactive Dashboard for COVID-19 Deaths", style={'text-align': 'center'}),

    dcc.DatePickerRange(
        id='deaths-date-picker-range',
        start_date='2020-01-22',
        end_date='2023-07-23',
        display_format='YYYY-MM-DD',
        min_date_allowed='2020-01-22',
        max_date_allowed='2023-07-23',
    ),
    
    dcc.RadioItems(
        id='deaths-y-axis-scale',
        options=[
            {'label': 'Linear Scale', 'value': 'linear'},
            {'label': 'Log Scale', 'value': 'log'},
        ],
        value='linear',
        labelStyle={
            'display': 'block',
            'font-size': '20px'
        },
    ),
    
    dcc.Graph(id='deaths-graph', style={

        'border-style': 'solid',
        'border-width': '5px'
    }),

])


@app.callback(
    Output('cases-graph', 'figure'),
    [Input('cases-date-picker-range', 'start_date'),
     Input('cases-date-picker-range', 'end_date'),
     Input('cases-y-axis-scale', 'value')]
)

def update_cases_graph(start_date, end_date, y_axis_scale):
    selected_date_columns = [col for col in cases.columns if start_date <= col <= end_date]
    cases_df = cases[selected_date_columns]
    
    date_range = pd.date_range(start=start_date, end=end_date)
    
    daily_cases = []
    for col in cases.columns:
        daily_cases.append(cases[col].sum())
    daily_cases_data = pd.Series(daily_cases)
    
    days = np.arange(len(daily_cases_data))
    
    poly = PolynomialFeatures(degree=4)
    X_poly = poly.fit_transform(days.reshape(-1, 1))

    pr_cases = LinearRegression()
    pr_cases.fit(X_poly, daily_cases_data)
    cases_poly_predictions = pr_cases.predict(X_poly)

    if y_axis_scale == 'log':
        figure = {
        'data': [
            {'x': list(range(len(date_range))), 'y': np.log(cases_df.sum()), 'type': 'line', 'name': 'Cases'},
            {'x': list(range(len(date_range))), 'y': np.log(cases_poly_predictions), 'type': 'line', 'name': 'Predicted Cases', 'line': {'dash': 'dash'}}
            
        ],
        'layout': {
            'title': f'COVID-19 Cases from {start_date} to {end_date}',
            'xaxis': {'title': 'Days'},
            'yaxis': {'title': 'Number of Cases'}
            }
        }
    else:
        figure = {
        'data': [
            {'x': list(range(len(date_range))), 'y': cases_df.sum(), 'type': 'line', 'name': 'Cases'},
            {'x': list(range(len(date_range))), 'y': cases_poly_predictions, 'type': 'line', 'name': 'Predicted Cases', 'line': {'dash': 'dash'}}
            
        ],
        'layout': {
            'title': f'COVID-19 Cases from {start_date} to {end_date}',
            'xaxis': {'title': 'Days'},
            'yaxis': {'title': 'Number of Cases'}
            }
        }
        

    return figure

@app.callback(
    Output('deaths-graph', 'figure'),
    [Input('deaths-date-picker-range', 'start_date'),
     Input('deaths-date-picker-range', 'end_date'),
     Input('deaths-y-axis-scale', 'value')]
)
def update_deaths_graph(start_date, end_date, y_axis_scale):
    selected_date_columns = [col for col in cases.columns if start_date <= col <= end_date]
    
    deaths_df = deaths[selected_date_columns]
    
    date_range = pd.date_range(start=start_date, end=end_date)
    
    daily_deaths = []
    for col in deaths.columns:
        daily_deaths.append(deaths[col].sum())
    daily_deaths_data = pd.Series(daily_deaths)
    
    days = np.arange(len(daily_deaths_data))
    
    poly = PolynomialFeatures(degree=4)
    X_poly = poly.fit_transform(days.reshape(-1, 1))
    
    pr_deaths = LinearRegression()
    pr_deaths.fit(X_poly, daily_deaths_data)
    deaths_poly_predictions = pr_deaths.predict(X_poly)

    if y_axis_scale == 'log':
        figure = {
        'data': [
            {'x': list(range(len(date_range))), 'y': np.log(deaths_df.sum()), 'type': 'line', 'name': 'Deaths'},
            {'x': list(range(len(date_range))), 'y': np.log(deaths_poly_predictions), 'type': 'line', 'name': 'Predicted Deaths', 'line': {'dash': 'dash'}}
            
        ],
        'layout': {
            'title': f'COVID-19 Deaths from {start_date} to {end_date}',
            'xaxis': {'title': 'Days'},
            'yaxis': {'title': 'Number of Deaths'},
            }
        }
    else:
        figure = {
        'data': [
            {'x': list(range(len(date_range))), 'y': deaths_df.sum(), 'type': 'line', 'name': 'Deaths'},
            {'x': list(range(len(date_range))), 'y': deaths_poly_predictions, 'type': 'line', 'name': 'Predicted Deaths', 'line': {'dash': 'dash'}}
            
        ],
        'layout': {
            'title': f'COVID-19 Deaths from {start_date} to {end_date}',
            'xaxis': {'title': 'Days'},
            'yaxis': {'title': 'Number of Deaths'},
            }
        }
        

    return figure


