import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.plotly as py
import os
import copy
import time
import datetime
import json

import numpy as np
import pandas as pd
from flask_caching import Cache

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
                    id = 'salary_slider',
                    marks={i: {'label': ii, 'style':{'font-size':'150%'}} for i,ii in zip(db_app.EARNINGS,db_app.EARNING_LABLES)},
                    min=0,
                    max=db_app.EARNINGS[-1],
                    step=10000,
                    value=[db_app.EARNINGS[0], db_app.EARNINGS[-2]],
                ),
                html.Div([
                    html.H5(children='Select Year Range:'),
                    dcc.RangeSlider(
                    id = 'year_slider',
                    marks={i: {'label': int(i), 'style':{'font-size':'150%'}} for i in range(2008,2019)},
                    min=2008,
                    max=2018,
                    value=[2008, 2018],
                
                )],style={'margin-top':'3em'}),
                ],className=['container-fluid'],style={'margin-bottom':'4em', 'margin-top':0}),
                html.Div([dcc.Checklist(
                            id='inflation_ajust',
                            options=[{'label': i ,'value':i} for i in ['Adjust for Inflation']],
                            values=[],
                )],className=['col-sm-4'] ),
                html.Div([dcc.Checklist(
                            id='include_benefits',
                            options=[{'label': i ,'value':i} for i in ['Include Benefits']],
                            values=[],
                            
                )],className=['col-sm-4'] ),
                html.Div([dcc.Checklist(
                            id='include_salary',
                            options=[{'label': i ,'value':i} for i in ['Include Base Salary']],
                            values=['Include Base Salary'],
                            
                )],className=['col-sm-4'] ),
        ],className='col-sm-5'),
        html.Div([
          html.Div([
                  html.Div([
                      html.H5(children='Industry (leave blank for all):'),
                      dcc.Dropdown(
                                  id='sector_select',
                                  options=[{'label': i, 'value': i} for i in db_app.SECTORS]
                  )]),
                  html.Div([
                      html.H5(children='Company (leave blank for all):'),
                      dcc.Dropdown(
                                  id='companies_select'
                  )]),
                  html.Div([
                    html.H5(children='Job Category (leave blank for all):'),
                    dcc.Dropdown(
                        id='position_select',
                        options=[{'label': ii, 'value': i} for i, ii in zip(db_app.POSITIONS, db_app.POSITION_LABLES)],
                        value='',
                        clearable=True,

                   )]),
             ],className='container-fluid'),
        ],className='col-sm-3'),

        html.Div([
                html.Div ([
                    dcc.Graph(id='stacked_area',className=''),
                    ],style={'margin':0}),
        ],className='col-sm-4'),
    ],className='container-fluid well'),  

    html.Div([
        html.Div ([
           dcc.Graph(id='graph_counts',className=''),
        ],className=['col-sm-6']),

        html.Div ([
            dcc.Graph(id='graph_salaries',className=''),
        ],className=['col-sm-6']),
    ],className='container-fluid'),
    html.Div([
        html.Div([
            html.Div([
                 html.Div(id='results_box',className='summary') 

            ],className=['container-fluid']),
        ],className='col-sm-4'),
        html.Div([
            html.Div(id='sector_avg_box', className='summary'),
        ],className='col-sm-8'),
        # html.Div([
        #     html.Div(id='results_box', className='summary'),
        # ],className='col-sm-3'),
    ],className='container-fluid'),
    html.Div(id='intermediate-value',style={'display': 'None'}),
])


###############################################################################
# CALLBACKS
###############################################################################
@app.callback(
    Output(component_id='companies_select', component_property= 'options'),
    [Input(component_id='sector_select', component_property='value')])
def call1(value):
    temp = db_app.df[db_app.df._sector==value]
    options=[]
    ret1 = temp.employer.unique()
    ret1 = list(ret1)
    ret1.sort()
    for i in ret1:
        options.append({'label': i, 'value': i})
    return options

@app.callback(
    Output(component_id='companies_select', component_property='value'),
    [Input(component_id='sector_select', component_property='value')])
def call2(value):
    return 'None'


#################################################################################
# DATA PREPARATION
#################################################################################
@app.callback(
    Output('intermediate-value', 'children'),
    [Input(component_id='sector_select', component_property='value'),
    Input(component_id='year_slider', component_property='value'), 
    Input(component_id='companies_select', component_property='value'),
    Input(component_id='position_select', component_property='value'),
    Input(component_id='inflation_ajust', component_property='values'),
    Input(component_id='include_benefits', component_property='values'),
    Input(component_id='include_salary', component_property='values'),
    Input(component_id='salary_slider', component_property='value')])
def clean_data(sector,value1, value2, position, inflation, benefits, salary, salaries):

    df_temp = db_app.df.copy()

    if position!='' and position!= None:
        if position=='chief':
            df_temp=df_temp[df_temp.job_category2=='chief']
        else :
            df_temp=df_temp[df_temp.job_category1==position]
        
    # raise ValueError(df_temp.shape[0], 23)
    if (sector != None):
        df_temp = df_temp[df_temp._sector == sector]
        # raise ValueError(df_temp.shape, 23)
    else:
        sector = "All Industries"

    if ( str(value2) != 'None'):
        df_temp = df_temp[df_temp.employer==value2]
    else:
        value2 = "All Companies"

    if df_temp.shape[0]==0:
        return ""
    else:

        earn_column = fun.get_earnings_column(inflation, salary, benefits)
        if earn_column=="":
            return ""

        df_temp =  df_temp[df_temp.c_year >= int(value1[0])]
        df_temp =  df_temp[df_temp.c_year <= int(value1[1])]

        if df_temp.shape[0]==0 :
            return ""

        df_temp = df_temp[df_temp[earn_column]>=salaries[0]]
        if (salaries[1]<600000):
            df_temp = df_temp[df_temp[earn_column]<=salaries[1]]

        if df_temp.shape[0]==0:
                return ""

        df_temp = pd.DataFrame(df_temp.groupby(['c_year','_gender_x']).agg({'first_name':len, earn_column:np.mean}))
        df_temp.reset_index(inplace=True)

        df_temp.columns=['c_year','_gender_x','first_name','salary_x']

        df_m= df_temp[df_temp._gender_x.astype(str)=='male']
        df_f= df_temp[df_temp._gender_x.astype(str)=='female']

        datasets = {
            'df_m': df_m.to_json(orient='split', date_format='iso'),
            'df_f': df_f.to_json(orient='split', date_format='iso')
        }

        return json.dumps(datasets)    

# @app.callback(
#     Output(component_id='summary_box', component_property='children'),
#     [Input(component_id='sector_select', component_property='value'),
#     Input(component_id='year_slider', component_property='value'), 
#     Input(component_id='companies_select', component_property='value'),
#     Input(component_id='position_select', component_property='value'),
#     Input(component_id='inflation_ajust', component_property='values'),
#     Input(component_id='include_benefits', component_property='values'),
#     Input(component_id='include_salary', component_property='values'),
#     Input(component_id='salary_slider', component_property='value')])
# def displayParameterSummary(sector,value1, value2, position, inflation, benefits, salary, salaries):
#     if sector==None:
#         sector = "All Industries"
#     if value2==None or value2=='None':
#         value2 = "All Companies"
#     if len(inflation)==0:
#         inflation=['Not Adjusted']
#     else:
#         inflation=['Adjusted']
#     if len(benefits)==0:
#         benefits='Not Included'
#     else:
#         benefits='Included'
#     if len(salary)==0:
#         salary='Not Included'
#     else:
#         salary='Included'

#     if position =='none':
#         position = 'All positions'
#     elif position=='chief':
#         position = 'Chiefs'
#     elif position=='vp':
#         position = 'VPs'
#     elif position=='ceo':
#         position = 'CEOs'
#     elif position=='cfo':
#         position = 'CFOs'
#     elif position=='cto':
#         position = 'CTOs'
#     elif position=='chro':
#         position = 'CHROs'

#     temp = []
#     temp.append(["Years", str(value1[0]) + " - " + str(value1[1])])
#     if (salaries[1]==600000):
#         temp.append(["Salary Range", "from " + "{:,}".format(salaries[0]) ])
#     else:
#         temp.append(["Salary Range", "{:,}".format(salaries[0]) + " - " + "{:,}".format(salaries[1])])

#     temp.append(["Industry", str(sector)])
#     temp.append(["Company", str(value2)])
#     temp.append(["Positions", position])
#     temp.append(["Adjusted to Inflation", str(inflation[0])])
#     temp.append(["Base Salary Included", str(salary)])
#     temp.append(["Benefits Included", str(benefits)])
#     temp_df = pd.DataFrame(temp)

#     return fun.generate_table(temp_df, title = 'Parameters Summary',display_columns=False)

@app.callback(
    Output(component_id='sector_avg_box', component_property='children'),
    [Input(component_id='sector_select', component_property='value'),
    Input(component_id='year_slider', component_property='value'), 
    Input(component_id='inflation_ajust', component_property='values'),
    Input(component_id='include_benefits', component_property='values'),
    Input(component_id='include_salary', component_property='values'),
    Input(component_id='salary_slider', component_property='value')])
def displaySectorSummary(sector,value1, inflation, benefits, salary, salaries):

    df_temp = db_app.df.copy()

    if (sector != None):
        df_temp = df_temp[df_temp._sector == sector]
        # raise ValueError(df_temp.shape, 23)
    else:
        sector = "All Industries"

    if df_temp.shape[0]==0:
        return ""
    else:

        earn_column = fun.get_earnings_column(inflation, salary, benefits)
        if earn_column=="":
            return ""

        df_temp =  df_temp[df_temp.c_year >= int(value1[0])]
        df_temp =  df_temp[df_temp.c_year <= int(value1[1])]

        if df_temp.shape[0]==0 :
            return ""

        df_temp = df_temp[df_temp[earn_column]>=salaries[0]]
        if (salaries[1]<600000):
            df_temp = df_temp[df_temp[earn_column]<=salaries[1]]

        if df_temp.shape[0]==0:
                return ""

        df_temp = pd.DataFrame(df_temp.groupby(['_gender_x','_sector']).agg({'first_name':len, earn_column:np.mean}))
        df_temp.reset_index(inplace=True)
        df_m= df_temp[df_temp._gender_x.astype(str)=='male']
        df_f= df_temp[df_temp._gender_x.astype(str)=='female']
        dd = pd.merge(df_m,df_f, how='outer', left_on='_sector', right_on="_sector")
        dd.drop(columns=['_gender_x_x','_gender_x_y'],inplace=True)
        dd.columns = ['_sector','m_count','m_salary','f_count','f_salary']

        dd['per_female'] = fun.get_f_count_number(dd.f_count, dd.m_count)
        # dd.apply(lambda x: x.f_count/(x.f_count+x.m_count)*100, axis=1)
        dd['per_female_salary'] = 0

        dd['per_female_salary'] = fun.get_f_count_number(dd.f_salary, dd.m_salary)
        # dd.apply(lambda x: x.f_salary/(x.f_salary+x.m_salary)*100, axis=1)

        dd = dd.reindex(columns=['_sector','m_count','f_count','per_female','m_salary','f_salary','per_female_salary'])
        dd.fillna(0, inplace=True)
        dd.columns = ['Industry','# of Male','# of Female', '% of Female','Male Earnings','Female Earnings','% of Female Earnings']

    return fun.generate_table(dd, title='Averages by Industry',  dtypes = ["","num","num","per","dol","dol","per"])

@app.callback(
    Output(component_id='results_box', component_property='children'),
    [Input('intermediate-value', 'children')])
def displayGraphSummary(value):
    if value == "":
            return html.Div(children = 'No Results Returned',className= ['alert alert-info'])

    datasets = json.loads(value)

    df_m= pd.read_json(datasets['df_m'], orient='split')
    df_f= pd.read_json(datasets['df_f'], orient='split')

    f_count = df_f.first_name.sum()
    m_count = df_m.first_name.sum()

    f_salary = 0
    if f_count>0:
        f_salary = round(df_f.salary_x.mean(),2)

    m_salary = 0
    if m_count>0:
        m_salary = round(df_m.salary_x.mean(),2)

    per_female = 0
    if (f_count>0):
        per_female = round(f_count/(f_count+m_count)*100,2)
    per_female_salary  = 0
    if f_count > 0:
        per_female_salary = round(f_salary/(f_salary+m_salary)*100,2)

    temp = []
    temp.append(["Male Employees Count", "{:,}".format(m_count)])
    temp.append(["Male Average Earnings", "$"+"{:,}".format(m_salary)])
    temp.append(["",""])
    temp.append(["# of Female Employees", "{:,}".format(f_count)])
    temp.append(["Female Average Earnings", "$"+"{:,}".format(f_salary)])
    temp.append(["",""])
    temp.append(["# of Females", str(per_female) + "%"])
    temp.append(["Female Salaries", str(per_female_salary) + "%"])

    temp_df = pd.DataFrame(temp)
    return fun.generate_table(temp_df, title = "Graphs Summary", display_columns=False)


###############################################################################
# CALLBACKS: GRAPHS
###############################################################################

@app.callback(
    Output(component_id='stacked_area', component_property='figure'),
    [Input('intermediate-value', 'children')])
def call3_stacked_area(value):
    
    if value == "":
        return {}

    datasets = json.loads(value)

    df_m= pd.read_json(datasets['df_m'], orient='split')
    df_f= pd.read_json(datasets['df_f'], orient='split')

    xx =  {
            'data': [
                {'x': df_m.c_year, 'y': df_m.first_name,  'name': 'Male','stackgroup':'one','fillcolor':db_app.COLORS['cmale']},
                {'x': df_f.c_year, 'y': df_f.first_name,  'name': 'Female','stackgroup':'one','fillcolor':db_app.COLORS['cfemale']},
            ],
            'layout' : {
                'title':'Employees Counts',   
                'margin':{'t':30,'r':20,'l':50,'b':50},
                'height': 260,
                'showlegend':True,
                'legend':{'orientation':"h"},
                    'xaxis':dict(
                            type='category',
                        ),
                    'yaxis':dict(
                            title = 'Male vs Female',
                            type='linear', showticklabels=False,gridcolor='black', gridwidth=0.2
                        )
                    }
            }
    return xx

@app.callback(
    Output(component_id='graph_counts', component_property='figure'),
    [Input('intermediate-value', 'children')])
def call3(value):
    if value == "":
        return {}

    datasets = json.loads(value)

    df_m= pd.read_json(datasets['df_m'], orient='split')
    df_f= pd.read_json(datasets['df_f'], orient='split')

    return {
            'data': [
                {'x': df_m.c_year, 'y': df_m.first_name, 'type': 'bar', 'name': 'Male','textposition':'inside',
                'insidetextfont':{'size':20}, 'textfont':{'size':20},
                'text': fun.get_m_count(df_f.first_name, df_m.first_name), 
                'marker':{'color':db_app.COLORS['cmale']}},
                {'x': df_f.c_year, 'y': df_f.first_name, 'type': 'bar', 'name': 'Female','textposition':'inside', 
                'insidetextfont':{'size':20},
                'text': fun.get_f_count(df_f.first_name, df_m.first_name), 
                'marker':{'color':db_app.COLORS['cfemale']}},
            ],
            'layout': {
                'title':'Employees Counts',
                'plot_bgcolor': db_app.COLORS['background'],
                'paper_bgcolor': db_app.COLORS['background'],
                'font': {
                    'color': db_app.COLORS['text'],
                    'size':'120%'},
                'xaxis':dict(tickvals = db_app.YEARS, 
                    ticktext = db_app.YEARS),
                'yaxis':dict(title = 'Employee Count',gridcolor='white', gridwidth=0.5)
            }
        }

@app.callback(
    Output(component_id='graph_salaries', component_property='figure'),
    [Input('intermediate-value', 'children')])
def call4(value):
    if value == "":
        return {}

    datasets = json.loads(value)

    df_m= pd.read_json(datasets['df_m'], orient='split')
    df_f= pd.read_json(datasets['df_f'], orient='split')
    return {
            'data': [
                {'x': df_m.c_year, 'y': df_m.salary_x, 'type': 'bar', 'name': 'Male',
                'marker':{'color':db_app.COLORS['cmale']}},
                {'x': df_f.c_year, 'y': df_f.salary_x, 'type': 'bar', 'name': 'Female',
                'marker':{'color':db_app.COLORS['cfemale']}},
            ],
            'layout':
            {
                'title':'Average Earnings Comparison',
                'plot_bgcolor': db_app.COLORS['background'],
                'paper_bgcolor': db_app.COLORS['background'],
                
                'font': {
                    'color': db_app.COLORS['text'],
                    'size':'120%'},
                'xaxis':dict(tickvals = db_app.YEARS, 
                    ticktext = db_app.YEARS),
                'yaxis':dict(title = 'Canadian $', gridcolor='white', gridwidth=0.5),

            }
        }
