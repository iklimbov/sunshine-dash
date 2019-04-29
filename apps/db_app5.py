import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import numpy as np
import pandas as pd

from db_app import app
import db_app
import functions as fun


###############################################################################
# HTML layout
###############################################################################
layout = html.Div(children=[
    html.Div([
      html.Iframe(src='/about', className='about_frame'), 
    ],className='container-fluid'), 
    html.Div(id='placeholder5',style={'display': 'None'}),
    html.Div(id='footer5')
])

###############################################################################
# Page footer
###############################################################################
@app.callback(
    Output(component_id='footer5', component_property= 'children'),
    [Input('placeholder5', 'value')])
def call1(value):
    return fun.get_footer()

