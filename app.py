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
import dash_daq as daq
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

    daq.BooleanSwitch(
        id='accumulated_switch',
        on=False,
        label="Accumulate Data",
        labelPosition="top",
    ),

    daq.BooleanSwitch(
        id='case_death_switch',
        on=False,
        label="Cases/Deaths",
        labelPosition="top",
    ),

])


@app.callback(
    Output('cases-graph', 'figure'),
    [Input('cases-date-picker-range', 'start_date'),
     Input('cases-date-picker-range', 'end_date'),
     Input('cases-y-axis-scale', 'value'),
     Input('accumulated_switch', 'value'),
     Input('case_death_switch', 'value')]
)

def update_cases_graph(start_date, end_date, y_axis_scale, accumulated_switch, case_death_switch):
    dataset = cases if case_death_switch else deaths
    selected_date_columns = [col for col in cases.columns if start_date <= col <= end_date]
    df = dataset[selected_date_columns]
    
    date_range = pd.date_range(start=start_date, end=end_date)
    
    # daily_cases = []
    # for col in cases.columns:
    #     daily_cases.append(cases[col].sum())
    # daily_cases_data = pd.Series(daily_cases)
    
    # days = np.arange(len(daily_cases_data))
    
    # poly = PolynomialFeatures(degree=4)
    # X_poly = poly.fit_transform(days.reshape(-1, 1))

    # pr_cases = LinearRegression()
    # pr_cases.fit(X_poly, daily_cases_data)
    # cases_poly_predictions = pr_cases.predict(X_poly)

    if y_axis_scale == 'log':
        figure = {
        'data': [
            {'x': list(range(len(date_range))), 'y': np.log(df.sum()), 'type': 'line', 'name': 'Cases'},
            # {'x': list(range(len(date_range))), 'y': np.log(cases_poly_predictions), 'type': 'line', 'name': 'Predicted Cases', 'line': {'dash': 'dash'}}
            
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
            {'x': list(range(len(date_range))), 'y': df.sum(), 'type': 'line', 'name': 'Cases'},
            # {'x': list(range(len(date_range))), 'y': cases_poly_predictions, 'type': 'line', 'name': 'Predicted Cases', 'line': {'dash': 'dash'}}
            
        ],
        'layout': {
            'title': f'COVID-19 Cases from {start_date} to {end_date}',
            'xaxis': {'title': 'Days'},
            'yaxis': {'title': 'Number of Cases'}
            }
        }
        

    return figure


