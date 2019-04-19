import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

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
                    id = 'salary_slider2',
                    marks={i: {'label': ii, 'style':{'font-size':'150%'}} for i,ii in zip(db_app.EARNINGS,db_app.EARNING_LABLES)},
                    min=0,
                    max=db_app.EARNINGS[-1],
                    step=10000,
                    value=[db_app.EARNINGS[0], db_app.EARNINGS[-2]],
                )],className=['container-fluid'],style={'margin-bottom':'4em', 'margin-top':0}),
                html.Div([dcc.Checklist(
                            id='inflation_ajust2',
                            options=[{'label': i ,'value':i} for i in ['Adjust for Inflation']],
                            values=[],
                )],className=['col-sm-4'] ),
                html.Div([dcc.Checklist(
                            id='include_benefits2',
                            options=[{'label': i ,'value':i} for i in ['Include Benefits']],
                            values=[],
                            
                )],className=['col-sm-4'] ),
                html.Div([dcc.Checklist(
                            id='include_salary2',
                            options=[{'label': i ,'value':i} for i in ['Include Base Salary']],
                            values=['Include Base Salary'],
                            
                )],className=['col-sm-4'] ),
        ],className='col-sm-6'),
        html.Div([
          html.Div([

                  html.Div([
                    html.H5(
                        children='Job Category (leave blank for all):'),
                    dcc.Dropdown(
                        id='position_select2',
                        options=[{'label': ii, 'value': i} for i, ii in zip(db_app.POSITIONS, db_app.POSITION_LABLES)],
                        value='',
                        clearable=True,

                   )]),
                  
             ],className='container-fluid'),
        ],className='col-sm-3'),
        html.Div([
            html.Div([
                  html.Div([
                      html.H5(children='Industry (leave blank for all):'),
                      dcc.Dropdown(
                                  id='sector_select2',
                                  options=[{'label': i, 'value': i} for i in db_app.SECTORS]
                  )]),
                  html.Div([
                      html.H5(children='Company (leave blank for all):'),
                      dcc.Dropdown(
                                  id='companies_select2'
                  )]),

            ],className=['container-fluid']),
        ],className='col-sm-3'),
    ],className='container-fluid well'),  
    html.Div([
        html.Div ([
           dcc.Graph(id='dist_graph'),
        ],className=['col-sm-4']),
        html.Div ([
            dcc.Graph(id='dist_graph1'),
        ],className=['col-sm-4']),
        html.Div ([
            dcc.Graph(id='dist_graph2'),
        ],className=['col-sm-4']),
    ],className='col-sm-12 container-fluid'),
    html.Div([
        html.Div ([
            html.Div(id='dist_summary1',className='summary'),
        ],className=['col-sm-4']),
        html.Div ([
            html.Div(id='dist_summary2',className='summary'),
        ],className=['col-sm-4']),
        html.Div ([
            html.Div(id='dist_summary3',className='summary'),
        ],className=['col-sm-4']),
    ],className='col-sm-12 container-fluid'),

    html.Div([
        html.Div(id='dedug-out',style={'display': 'None'}),
    ],className=['col-sm-12 panel panel-default'])

])


###############################################################################
# CALLBACKS: GRAPHS
###############################################################################
@app.callback(
    Output(component_id='dist_graph', component_property='figure'),
    [Input(component_id='position_select2', component_property='value'),
    Input(component_id='inflation_ajust2', component_property='values'),
    Input(component_id='include_benefits2', component_property='values'),
    Input(component_id='include_salary2', component_property='values'),
    Input(component_id='salary_slider2', component_property='value')])
def cbg1(position, inflation, benefits, salary, salaries):

    df_temp = db_app.df18.copy()

    if position!='' and position!=None:
        if position=='chief':
            df_temp=df_temp[df_temp.job_category2=='chief']
        else :
            df_temp=df_temp[df_temp.job_category1==position]

    if df_temp.shape[0]==0:
        return ""
    else:

        earn_column = fun.get_earnings_column(inflation, salary, benefits)
        if earn_column=="":
            return ""

        if df_temp.shape[0]==0 :
            return ""

        df_temp = df_temp[df_temp[earn_column]>=salaries[0]]
        if (salaries[1]<600000):
            df_temp = df_temp[df_temp[earn_column]<=salaries[1]]

        if df_temp.shape[0]==0:
                return ""

        df_temp = df_temp[['_gender_x','first_name',earn_column]]
        df_temp.columns=['_gender_x','first_name','salary_x']

        df_m= df_temp[df_temp._gender_x.astype(str)=='male']
        df_f= df_temp[df_temp._gender_x.astype(str)=='female']

    return fun.format_dist_graph_data(df_f, df_m, "Salary Distribution")

@app.callback(
    Output(component_id='dist_graph1', component_property='figure'),
    [Input(component_id='sector_select2', component_property='value'),
    Input(component_id='position_select2', component_property='value'),
    Input(component_id='inflation_ajust2', component_property='values'),
    Input(component_id='include_benefits2', component_property='values'),
    Input(component_id='include_salary2', component_property='values'),
    Input(component_id='salary_slider2', component_property='value')])
def cbg2(sector, position, inflation, benefits, salary, salaries):
    if (sector==None):
        return {
                'layout': {
                    'visible':'legendonly',
                    'title': "All Companies for Selected Industry",
                    'margin':{'t':'1em','r':1,'l':1,'b':20},
                    'height': 600,
                    'legend':{'orientation':"h"}
                }}

    df_temp = db_app.df18.copy()

    if position!='' and position!=None:
        if position=='chief':
            df_temp=df_temp[df_temp.job_category2=='chief']
        else :
            df_temp=df_temp[df_temp.job_category1==position]

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

        if df_temp.shape[0]==0 :
            return ""

        df_temp = df_temp[df_temp[earn_column]>=salaries[0]]
        if (salaries[1]<600000):
            df_temp = df_temp[df_temp[earn_column]<=salaries[1]]

        if df_temp.shape[0]==0:
                return ""

        df_temp = df_temp[['_gender_x','first_name',earn_column]]
        df_temp.columns=['_gender_x','first_name','salary_x']

        df_m= df_temp[df_temp._gender_x.astype(str)=='male']
        df_f= df_temp[df_temp._gender_x.astype(str)=='female']

    return  fun.format_dist_graph_data(df_f, df_m, "Salary Distribution. " + sector)

@app.callback(
    Output(component_id='dist_graph2', component_property='figure'),
    [Input(component_id='sector_select2', component_property='value'),
    Input(component_id='companies_select2', component_property='value'),
    Input(component_id='position_select2', component_property='value'),
    Input(component_id='inflation_ajust2', component_property='values'),
    Input(component_id='include_benefits2', component_property='values'),
    Input(component_id='include_salary2', component_property='values'),
    Input(component_id='salary_slider2', component_property='value')])
def cbg3(sector, value2, position, inflation, benefits, salary, salaries):
    if (value2==None or sector==None or value2=='None'):
        return {
        'layout': {
            'visible':'legendonly',
            'title': "Selected Company",
            'margin':{'t':'1em','r':1,'l':1,'b':20},
            'height': 600,
            'legend':{'orientation':"h"}
        }}

    df_temp = db_app.df18.copy()

    if position!='' and position!=None:
        if position=='chief':
            df_temp=df_temp[df_temp.job_category2=='chief']
        else :
            df_temp=df_temp[df_temp.job_category1==position]

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

        if df_temp.shape[0]==0 :
            return ""

        df_temp = df_temp[df_temp[earn_column]>=salaries[0]]
        if (salaries[1]<600000):
            df_temp = df_temp[df_temp[earn_column]<=salaries[1]]

        if df_temp.shape[0]==0:
                return ""

        df_temp = df_temp[['_gender_x','first_name',earn_column]]
        df_temp.columns=['_gender_x','first_name','salary_x']

        df_m= df_temp[df_temp._gender_x.astype(str)=='male']
        df_f= df_temp[df_temp._gender_x.astype(str)=='female']

    return  fun.format_dist_graph_data(df_f, df_m, "Salary Distribution. " + value2)


###############################################################################
# SUMMARY BOX 1
###############################################################################
@app.callback(
    Output(component_id='dist_summary1', component_property='children'),
    [Input(component_id='position_select2', component_property='value'),
    Input(component_id='inflation_ajust2', component_property='values'),
    Input(component_id='include_benefits2', component_property='values'),
    Input(component_id='include_salary2', component_property='values')])
def sb1_adjust( position, inflation, benefits, salary):
    df_temp = db_app.df18.copy()

    if position!='' and position!=None:
        if position=='chief':
            df_temp=df_temp[df_temp.job_category2=='chief']
        else :
            df_temp=df_temp[df_temp.job_category1==position]

    if df_temp.shape[0]==0:
        return ""
    else:

        earn_column = fun.get_earnings_column(inflation, salary, benefits)
        if earn_column=="":
            return ""
        if df_temp.shape[0]==0 :
            return ""

        df_temp = df_temp[['_gender_x','first_name',earn_column]]
        df_temp.columns=['_gender_x','first_name','salary_x']

    
        df_temp['quantiles']=1
        try:
            df_temp['quantiles']=pd.qcut(df_temp.salary_x.rank(method='first'), 10)
        except:
            pass


        df_temp = pd.DataFrame(df_temp.groupby(['_gender_x','quantiles']).agg({'first_name':len, 'salary_x':[np.mean,np.min,np.max], }))
        df_temp.reset_index(inplace=True)


        df_temp.columns=['_gender_x','quantiles','first_name','salary_x', 'salary_min', 'salary_max']
        df_temp.salary_x = df_temp.salary_x.astype(int)
        df_temp.salary_min = df_temp.salary_min.astype(int)
        df_temp.salary_max = df_temp.salary_max.astype(int)

        df_temp = pd.merge(df_temp[df_temp._gender_x=='female'],df_temp[df_temp._gender_x=='male'], how='inner',left_on='quantiles', right_on='quantiles' )
        # df_temp['range'] = df_temp[['salary_min_x','salary_min_y']].min(axis=1).astype(str) + " - " + df_temp[['salary_max_x','salary_max_y']].max(axis=1).astype(str)
        df_temp['range'] = [i for i in range(1,df_temp.shape[0]+1)]
        
        df_temp['per_female'] = fun.get_f_count_number(df_temp.first_name_x, df_temp.first_name_y)
        df_temp['per_female_salary'] = fun.get_f_count_number(df_temp.salary_x_x, df_temp.salary_x_y)
        df_temp = df_temp[['range','first_name_x','first_name_y','per_female','salary_x_x','salary_x_y', 'per_female_salary']]
        df_temp.columns = ['Decile','# of Female','# of Male','% of Female','Salary Female','Salary Male','% of Female Salary']

    return fun.generate_table(df_temp, title = "Decile Summary.  All Industries", display_columns=True, 
        dtypes = ["","num","num","per","num","num","per"])

###############################################################################
# SUMMARY BOX 2
###############################################################################
@app.callback(
    Output(component_id='dist_summary2', component_property='children'),
    [Input(component_id='sector_select2', component_property='value'),
    Input(component_id='position_select2', component_property='value'),
    Input(component_id='inflation_ajust2', component_property='values'),
    Input(component_id='include_benefits2', component_property='values'),
    Input(component_id='include_salary2', component_property='values')])
def sb2_adjust(sector, position, inflation, benefits, salary):

    if (sector==None):
        return ""
    df_temp = db_app.df18.copy()

    if position!='' and position!=None:
        if position=='chief':
            df_temp=df_temp[df_temp.job_category2=='chief']
        else :
            df_temp=df_temp[df_temp.job_category1==position]

    if (sector != None):
        df_temp = df_temp[df_temp._sector == sector]
    else:
        sector = "All Industries"
    if df_temp.shape[0]==0:
        return ""
    else:
        
        earn_column = fun.get_earnings_column(inflation, salary, benefits)
        if earn_column=="":
            return ""

        if df_temp.shape[0]==0 :
            return ""

        df_temp = df_temp[['_gender_x','first_name',earn_column]]
        df_temp.columns=['_gender_x','first_name','salary_x']
        
        df_temp['quantiles']=1
        try:
            df_temp['quantiles']=pd.qcut(df_temp.salary_x.rank(method='first'), 10)
        except:
            pass

        df_temp = pd.DataFrame(df_temp.groupby(['_gender_x','quantiles']).agg({'first_name':len, 'salary_x':[np.mean,np.min,np.max], }))
        df_temp.reset_index(inplace=True)


        df_temp.columns=['_gender_x','quantiles','first_name','salary_x', 'salary_min', 'salary_max']
        df_temp.salary_x = df_temp.salary_x.astype(int)
        df_temp.salary_min = df_temp.salary_min.astype(int)
        df_temp.salary_max = df_temp.salary_max.astype(int)
        df_temp = pd.merge(df_temp[df_temp._gender_x=='female'],df_temp[df_temp._gender_x=='male'], how='inner',left_on='quantiles', right_on='quantiles' )
        # df_temp['range'] = df_temp[['salary_min_x','salary_min_y']].min(axis=1).astype(str) + " - " + df_temp[['salary_max_x','salary_max_y']].max(axis=1).astype(str)
        df_temp['range'] = [i for i in range(1,df_temp.shape[0]+1)]

        df_temp['per_female'] = fun.get_f_count_number(df_temp.first_name_x, df_temp.first_name_y)
        df_temp['per_female_salary'] = fun.get_f_count_number(df_temp.salary_x_x, df_temp.salary_x_y)
        df_temp = df_temp[['range','first_name_x','first_name_y','per_female','salary_x_x','salary_x_y', 'per_female_salary']]
        df_temp.columns = ['Decile','# of Female','# of Male','% of Female','Salary Female','Salary Male','% of Female Salary']
        # raise ValueError(df_temp.shape, 23)


    return fun.generate_table(df_temp, title = "Decile Summary. " + str(sector), display_columns=True,
        dtypes = ["","num","num","per","num","num","per"])

###############################################################################
# SUMMARY BOX 3
###############################################################################
@app.callback(
    Output(component_id='dist_summary3', component_property='children'),
    [Input(component_id='sector_select2', component_property='value'),
    Input(component_id='companies_select2', component_property='value'),
    Input(component_id='position_select2', component_property='value'),
    Input(component_id='inflation_ajust2', component_property='values'),
    Input(component_id='include_benefits2', component_property='values'),
    Input(component_id='include_salary2', component_property='values')])
def sb3_adjust(sector, value2, position, inflation, benefits, salary):
    if (value2==None or sector==None or value2=='None'):
        return ""
    df_temp = db_app.df18.copy()

    if position!='' and position!=None:
        if position=='chief':
            df_temp=df_temp[df_temp.job_category2=='chief']
        else :
            df_temp=df_temp[df_temp.job_category1==position]

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

        if df_temp.shape[0]==0 :
            return ""

        df_temp = df_temp[['_gender_x','first_name',earn_column]]
        df_temp.columns=['_gender_x','first_name','salary_x']

        df_temp['quantiles']=1
        try:
            df_temp['quantiles']=pd.qcut(df_temp.salary_x.rank(method='first'), 10)
        except:
            pass

        df_temp = pd.DataFrame(df_temp.groupby(['_gender_x','quantiles']).agg({'first_name':len, 'salary_x':[np.mean,np.min,np.max], }))
        df_temp.reset_index(inplace=True)


        df_temp.columns=['_gender_x','quantiles','first_name','salary_x', 'salary_min', 'salary_max']
        df_temp.salary_x = df_temp.salary_x.astype(int)
        df_temp.salary_min = df_temp.salary_min.astype(int)
        df_temp.salary_max = df_temp.salary_max.astype(int)

        df_temp = pd.merge(df_temp[df_temp._gender_x=='female'],df_temp[df_temp._gender_x=='male'], how='inner',left_on='quantiles', right_on='quantiles' )
        # df_temp['range'] = df_temp[['salary_min_x','salary_min_y']].min(axis=1).astype(str) + " - " + df_temp[['salary_max_x','salary_max_y']].max(axis=1).astype(str)
        df_temp['range'] = [i for i in range(1,df_temp.shape[0]+1)]

        df_temp['per_female'] = fun.get_f_count_number(df_temp.first_name_x, df_temp.first_name_y)
        df_temp['per_female_salary'] = fun.get_f_count_number(df_temp.salary_x_x, df_temp.salary_x_y)
        df_temp = df_temp[['range','first_name_x','first_name_y','per_female','salary_x_x','salary_x_y', 'per_female_salary']]
        df_temp.columns = ['Decile','# of Female','# of Male','% of Female','Salary Female','Salary Male','% of Female Salary']

    return fun.generate_table(df_temp, title = "Decile Summary for "  + str(value2) , display_columns=True, 
        dtypes = ["","num","num","per","dol","dol","per"])


###############################################################################
# POPULATE COMPANIES BASED ON SECTOR SELECTED
###############################################################################
@app.callback(
    Output(component_id='companies_select2', component_property= 'options'),
    [Input(component_id='sector_select2', component_property='value')])
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
    Output(component_id='companies_select2', component_property='value'),
    [Input(component_id='sector_select2', component_property='value')])
def call2(value):
    return 'None'




       