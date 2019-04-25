import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import numpy as np
import pandas as pd
import json

from db_app import app
import db_app
import functions as fun


###############################################################################
# HTML layout
###############################################################################
layout = html.Div(children=[
    html.Div([
        html.Div([
            html.Div([
                html.H5(children='Select Income Range :'),
                dcc.RangeSlider(
                    id = 'salary_slider2a',
                    marks={i: {'label': ii, 'style':{'font-size':'150%'}} for i,ii in zip(db_app.EARNINGS,db_app.EARNING_LABLES)},
                    min=0,
                    max=db_app.EARNINGS[-1],
                    step=10000,
                    value=[db_app.EARNINGS[0], db_app.EARNINGS[-2]],
                )],className=['container-fluid'],style={'margin-bottom':'4em', 'margin-top':0}),
                html.Div([
                    html.H5(
                        children='Role (leave blank for all):'),
                    dcc.Dropdown(
                        id='position_select2a',
                        options=[{'label': ii, 'value': i} for i, ii in zip(db_app.POSITIONS, db_app.POSITION_LABLES)],
                        value='',
                        clearable=True,
                )]),
                html.H5(" "),html.H5(" "),
                html.Div([dcc.Checklist(
                            id='inflation_ajust2a',
                            options=[{'label': i ,'value':i} for i in ['Adjust for Inflation']],
                            values=[],
                )],className=['col-sm-4'] ),
                html.Div([dcc.Checklist(
                            id='include_benefits2a',
                            options=[{'label': i ,'value':i} for i in ['Benefits']],
                            values=[],
                            
                )],className=['col-sm-4'] ),
                html.Div([dcc.Checklist(
                            id='include_salary2a',
                            options=[{'label': i ,'value':i} for i in ['Salary']],
                            values=['Salary'],
                            
                )],className=['col-sm-4'] ),

        ],className='col-sm-4'),
        html.Div([
            html.Div([
                  html.Div([
                      html.H5(children='Sector I:'),
                      dcc.Dropdown(
                                  id='sector_select2a',
                                  clearable=True,
                                  options=[{'label': i, 'value': i} for i in db_app.SECTORS],
                                  # value = 'Universities'
                  )]),
                  html.Div([
                      html.H5(children='Employer I :'),                      
                      dcc.Dropdown(
                                  id='companies_select_1',
                                  clearable=True,
                                  # value = 'Trent University'
                  )]),
                  

            ],className=['container-fluid']),
        ],className='col-sm-4'),
        html.Div([
          html.Div([
                html.Div([
                      html.H5(children='Sector II:'),
                      dcc.Dropdown(
                                  id='sector_select2b',
                                  clearable=True,
                                  options=[{'label': i, 'value': i} for i in db_app.SECTORS],
                                  # value = 'Universities'
                )]),
                html.Div([
                  html.H5(children='Employer II:'),
                  dcc.Dropdown(
                              id='companies_select_2',
                              clearable=True,
                              # value= 'Ryerson University'
                )]),
             ],className='container-fluid'),
        ],className='col-sm-4'),

    ],className='container-fluid well'),  

    html.Div([       
            html.Div([
                html.H3(id = 'selecttion_1a_title'),
                html.Div ([
                    dcc.Graph(id='dist_graph1a'),
                ],className='container-fluid'),
                html.H3(id='selection_1b_title'), 
                html.Div ([
                    html.Div(id='dist_summary1a',className='summary'),
                ],className='container-fluid'),
            ],className="col-sm-12 container-fluid"),
        ],className=['col-sm-6']),

    html.Div([
            html.Div([
                html.H3(id = 'selecttion_2a_title'),
                html.Div ([
                    dcc.Graph(id='dist_graph2a'),
                ],className='container-fluid'),
                html.H3(id='selection_2b_title'), 
                html.Div ([
                    html.Div(id='dist_summary2a',className='summary'),
                ],className='container-fluid'),
            ],className="col-sm-12 container-fluid"),

        ],className=['col-sm-6']),
     

    # html.Div([
    #     html.Div(id='dedug-out',style={'display': 'None'}),
    # ],className=['col-sm-12 panel panel-default'])

])


###############################################################################
# CALLBACKS: GRAPHS
###############################################################################

###############################################################################
# Distribution graph - for the selected sector and company I
# takes into account earnings columns and position
###############################################################################
@app.callback(
    Output(component_id='dist_graph1a', component_property='figure'),
    [Input(component_id='sector_select2a', component_property='value'),
    Input(component_id='companies_select_1', component_property='value'),
    Input(component_id='position_select2a', component_property='value'),
    Input(component_id='inflation_ajust2a', component_property='values'),
    Input(component_id='include_benefits2a', component_property='values'),
    Input(component_id='include_salary2a', component_property='values'),
    Input(component_id='salary_slider2a', component_property='value')])
def gr2_1(sector, company, position, inflation, benefits, salary, salaries):
    return fun.create_dist_graph(sector, company, position, inflation, benefits, salary, salaries)

###############################################################################
# Distribution graph - for the selected sector and company II
# takes into account earnings columns and position
###############################################################################
@app.callback(
    Output(component_id='dist_graph2a', component_property='figure'),
    [Input(component_id='sector_select2b', component_property='value'),
    Input(component_id='companies_select_2', component_property='value'),
    Input(component_id='position_select2a', component_property='value'),
    Input(component_id='inflation_ajust2a', component_property='values'),
    Input(component_id='include_benefits2a', component_property='values'),
    Input(component_id='include_salary2a', component_property='values'),
    Input(component_id='salary_slider2a', component_property='value')])
def gr2_1(sector, company, position, inflation, benefits, salary, salaries):
    return fun.create_dist_graph(sector, company, position, inflation, benefits, salary, salaries)

###############################################################################
# SUMMARY BOX - for selected sector
# takes into account earnings columns and position
###############################################################################
@app.callback(
    Output(component_id='dist_summary1a', component_property='children'),
    [Input(component_id='sector_select2a', component_property='value'),
    Input(component_id='companies_select_1', component_property='value'),
    Input(component_id='position_select2a', component_property='value'),
    Input(component_id='inflation_ajust2a', component_property='values'),
    Input(component_id='include_benefits2a', component_property='values'),
    Input(component_id='include_salary2a', component_property='values'),
    Input(component_id='salary_slider2a', component_property='value')])
def sb2_adjust(sector, company, position, inflation, benefits, salary, salaries):
    return fun.create_dist_summary( sector, company, position, inflation, benefits, salary, salaries)

###############################################################################
# SUMMARY BOX - for selected company II
# takes into account earnings columns and position
###############################################################################
@app.callback(
    Output(component_id='dist_summary2a', component_property='children'),
    [Input(component_id='sector_select2b', component_property='value'),
    Input(component_id='companies_select_2', component_property='value'),
    Input(component_id='position_select2a', component_property='value'),
    Input(component_id='inflation_ajust2a', component_property='values'),
    Input(component_id='include_benefits2a', component_property='values'),
    Input(component_id='include_salary2a', component_property='values'),
    Input(component_id='salary_slider2a', component_property='value'),])
def sb3_adjust( sector, company, position, inflation, benefits, salary, salaries):
    return fun.create_dist_summary( sector, company, position, inflation, benefits, salary, salaries)


###############################################################################
# Returns first subtitle or an information box - selection 1
###############################################################################
@app.callback(
    Output(component_id='selecttion_1a_title', component_property='children'),
    [Input(component_id='sector_select2a', component_property='value'),
    Input(component_id='companies_select_1', component_property='value')])
def cbg2(sector, company1):
    
    if sector == None:
        return html.Div(children = 'Select Sector and Company I',className= ['alert alert-info'])
    txt = "Selection I: " + sector
    
    try:
        txt += ": " + company1
    except:
        pass
    return txt

###############################################################################
# Returns first subtitle or an information box - selection 2
###############################################################################
@app.callback(
    Output(component_id='selecttion_2a_title', component_property='children'),
    [Input(component_id='sector_select2b', component_property='value'),
    Input(component_id='companies_select_2', component_property='value')])
def cbg2(sector, company1):
    
    if sector == None:
        return html.Div(children = 'Select Sector and Company II',className= ['alert alert-info'])
    txt = "Selection II: " + sector
    
    try:
        txt += ": " + company1
    except:
        pass
    return txt

###############################################################################
# Returns second subtitle - selection I
###############################################################################
@app.callback(
    Output(component_id='selection_1b_title', component_property='children'),
    [Input(component_id='sector_select2a', component_property='value'),
    Input(component_id='companies_select_1', component_property='value'),])
def cbg2(sector, company1):
    
    if sector == None:
        return ""
    txt = "Quartile Summary for " + sector
    try:
        txt += ". " + company1
    except:
        pass
    return txt

###############################################################################
# Returns second subtitle - selection II
###############################################################################
@app.callback(
    Output(component_id='selection_2b_title', component_property='children'),
    [Input(component_id='sector_select2b', component_property='value'),
    Input(component_id='companies_select_2', component_property='value'),])
def cbg2(sector, company1):
    
    if sector == None:
        return ""
    txt = "Quartile Summary for " + sector
    try:
        txt += ". " + company1
    except:
        pass
    return txt


###############################################################################
# POPULATE COMPANIES I BASED ON SECTOR SELECTED
###############################################################################
@app.callback(
    Output(component_id='companies_select_1', component_property= 'options'),
    [Input(component_id='sector_select2a', component_property='value')])
def call1(value):
    return fun.get_companies_for_sector(value,db_app.df18)

@app.callback(
    Output(component_id='companies_select_1', component_property='value'),
    [Input(component_id='sector_select2a', component_property='value')])
def call22(value):
    if (value==None ):
        return None

###############################################################################
# POPULATE COMPANIES II BASED ON SECTOR SELECTED
###############################################################################
@app.callback(
    Output(component_id='companies_select_2', component_property= 'options'),
    [Input(component_id='sector_select2b', component_property='value')])
def call1(value):
    return fun.get_companies_for_sector(value,db_app.df18)

@app.callback(
    Output(component_id='companies_select_2', component_property='value'),
    [Input(component_id='sector_select2b', component_property='value')])
def call22(value):
    if (value==None ):
        return None


###############################################################################
# List of roles for this sector 
###############################################################################
@app.callback(
    Output(component_id='position_select2a', component_property= 'options'),
    [Input(component_id='sector_select2a', component_property='value')])
def call1(value):
    return fun.get_roles(value, db_app.df18)

@app.callback(
    Output(component_id='position_select2a', component_property= 'value'),
    [Input(component_id='sector_select2a', component_property='value'),
    Input(component_id='companies_select_1', component_property='value')])
def call11(value, value1):
    return None


       