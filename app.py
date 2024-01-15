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
    html.Div(
        children=html.Div([
            html.H1("Interactive Dashboard for COVID-19 Data",
                style={'text-align': 'center'}),

            html.H3("Select States"),
            
            html.Div(
                children=[
                    dcc.Dropdown(
                        id='state-selection',
                        options=dropdown_options,
                        multi=True,
                        style={'width': '200px'},
                        value=['US']
                    ),
                ],
                id='selection-wrapper'
            ),

            html.H3("Other Options"),

            html.Div(
                children=[
                    daq.BooleanSwitch(
                        id='log_linear_switch',
                        on=False,
                        label="Linear/Log",
                        labelPosition="top",
                        className='button-item',
                    ),

                    daq.BooleanSwitch(
                        id='accumulated_switch',
                        on=False,
                        label="Differentiate Data",
                        labelPosition="top",
                        className='button-item',
                    ),

                    daq.BooleanSwitch(
                        id='case_death_switch',
                        on=False,
                        label="Cases/Deaths",
                        labelPosition="top",
                        className='button-item',
                    ),                 
                ],
                id='button-wrapper'
            ),
            
            
        ], 
        id='parameter-box'
        ),      
    ),
    dcc.Graph(id='graph'), 
],
id='body-wrapper')


@app.callback(
    Output('graph', 'figure'),
    [Input('state-selection', 'value'),
     Input('log_linear_switch', 'on'),
     Input('accumulated_switch', 'on'),
     Input('case_death_switch', 'on')]
)

def update_graph(states, log_linear_switch, accumulated_switch, case_death_switch):
    # switch between Cases and Death Datasets
    df = deaths if case_death_switch else cases

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
        'title': f"{'' if accumulated_switch else 'Accumulated '}COVID-19 {'Deaths' if case_death_switch else 'Cases'} by Day{' in ' + state_dic[states[0]] if len(states) < 2 else ''}",
        'xaxis': {'title': 'Days'},
        'yaxis': {'title': f"{'New ' if accumulated_switch else ''}Number of {'Deaths' if case_death_switch else 'Cases'} {'in logarithm base 10' if log_linear_switch else ''}"}
        }
    }

    return figure


