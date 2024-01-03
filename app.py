from dash import Dash, dcc, html, Input, Output, callback
import os
import pandas as pd
import numpy as np
import plotly.graph_objs as go


# from sklearn.linear_model import LinearRegression
# from sklearn.preprocessing import PolynomialFeatures
from datetime import datetime as dt

import dash
from dash import dcc
import dash_daq as daq
from dash import html
from dash.dependencies import Input, Output 

# load data
cases = pd.read_csv('./data/cases.csv')
deaths = pd.read_csv('./data/deaths.csv')


column_list = ['State']
column_list.extend(list(cases.columns[4:]))

cases = cases[column_list].groupby(by=["State"]).sum()
cases.loc['US',:] = cases.sum(axis=0)

deaths = deaths[column_list].groupby(by=["State"]).sum()
deaths.loc['US',:] = deaths.sum(axis=0)

from state_dic import dropdown_options, state_dic

# dash app
app = Dash(__name__)

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

            dcc.Dropdown(
                id='cases-state-selection',
                options=dropdown_options,
                multi=True,
                style={'width': '200px'},
                value=['US']
            ),
    
            daq.BooleanSwitch(
                id='log_linear_switch',
                on=False,
                label="Linear",
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
     Input('cases-state-selection', 'value'),
     Input('log_linear_switch', 'on'),
     Input('accumulated_switch', 'on'),
     Input('case_death_switch', 'on')]
)

def update_graph(start_date, end_date, states, log_linear_switch, accumulated_switch, case_death_switch):
    # switch between Cases and Death Datasets
    dataset = deaths if case_death_switch else cases

    # select columns based on date selection

    selected_date_columns = [col for col in cases.columns if start_date <= col <= end_date]
    df = dataset[selected_date_columns]

    # differentiate data if needed
    if accumulated_switch: df = df.diff(axis=1)

    # use logarithmic scale
    if log_linear_switch: df = np.log10(df)

    # select states to graph
    if states == []: states = ['US'] # US as default for empty selection
    data = [{'x': df.loc[state].index, 'y': df.loc[state], 'type': 'line', 'name': state} for state in states]


    figure = {
    'data': data,
    'layout': {
        'title': f"{'' if accumulated_switch else 'Accumulated '}COVID-19 {'Deaths' if case_death_switch else 'Cases'} from {start_date} to {end_date}{' in ' + state_dic[states[0]] if len(states) < 2 else ''}",
        'xaxis': {'title': 'Days'},
        'yaxis': {'title': f"{'New ' if accumulated_switch else ''}Number of Cases {'in logarithm base 10' if log_linear_switch else ''}"}
        }
    }

    return figure


