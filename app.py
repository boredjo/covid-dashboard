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


cases = pd.read_csv('./data/cases.csv')
selected_date_columns = [col for col in cases.columns if '2020-01-22' <= col <= '2023-07-23']
cases = cases[selected_date_columns]

deaths = pd.read_csv('./data/deaths.csv')
selected_date_columns = [col for col in deaths.columns if '2020-01-22' <= col <= '2023-07-23']
deaths = deaths[selected_date_columns]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div([
    # header for css
    html.Div(
        className="app-header",
        children=[
            html.Div('Plotly Dash', className="app-header--title")
        ]
    ),
    html.Div(
        children=html.Div([
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
    
            daq.BooleanSwitch(
                id='log_linear_switch',
                on=False,
                label="Log/Linear",
                labelPosition="top",
            ),

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
    
            dcc.Graph(id='cases-graph', style={
                'border-style': 'solid',
                'border-width': '5px'
            }),
        ])
    )   
])


@app.callback(
    Output('cases-graph', 'figure'),
    [Input('cases-date-picker-range', 'start_date'),
     Input('cases-date-picker-range', 'end_date'),
     Input('log_linear_switch', 'on'),
     Input('accumulated_switch', 'on'),
     Input('case_death_switch', 'on')]
)

def update_graph(start_date, end_date, log_linear_switch, accumulated_switch, case_death_switch):
    # switch between Cases and Death Datasets
    dataset = cases if case_death_switch else deaths

    selected_date_columns = [col for col in cases.columns if start_date <= col <= end_date]
    df = dataset[selected_date_columns]

    # differentiate data if needed
    if accumulated_switch: df = df.diff(axis=1, periods=7)
    
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


    figure = {
    'data': [
        {'x': list(range(len(date_range))), 'y': np.log(df.sum()) if log_linear_switch else df.sum(), 'type': 'line', 'name': 'Cases'},
        # {'x': list(range(len(date_range))), 'y': np.log(cases_poly_predictions), 'type': 'line', 'name': 'Predicted Cases', 'line': {'dash': 'dash'}}
        
    ],
    'layout': {
        'title': f"{'' if accumulated_switch else 'Accumulated '}COVID-19 {'Cases' if case_death_switch else 'Deaths'} from {start_date} to {end_date}",
        'xaxis': {'title': 'Days'},
        'yaxis': {'title': f"{'New ' if accumulated_switch else ''}Number of Cases"}
        }
    }

    return figure


