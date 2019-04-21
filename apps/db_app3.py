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
                    id = 'salary_slider3',
                    marks={i: {'label': ii, 'style':{'font-size':'150%'}} for i,ii in zip(db_app.EARNINGS,db_app.EARNING_LABLES)},
                    min=0,
                    max=db_app.EARNINGS[-1],
                    step=10000,
                    value=[db_app.EARNINGS[0], db_app.EARNINGS[-2]],
                )],className=['container-fluid'],style={'margin-bottom':'4em', 'margin-top':0}),
                html.Div([dcc.Checklist(
                            id='inflation_ajust3',
                            options=[{'label': i ,'value':i} for i in ['Adjust for Inflation']],
                            values=[],
                )],className=['col-sm-4'] ),
                html.Div([dcc.Checklist(
                            id='include_benefits3',
                            options=[{'label': i ,'value':i} for i in ['Include Benefits']],
                            values=[],
                            
                )],className=['col-sm-4'] ),
                html.Div([dcc.Checklist(
                            id='include_salary3',
                            options=[{'label': i ,'value':i} for i in ['Include Base Salary']],
                            values=['Include Base Salary'],
                            
                )],className=['col-sm-4'] ),
        ],className='col-sm-6'),

        html.Div ([
           dcc.Graph(id='summary_pie', ),
           
        ], className='col-sm-3'),
        html.Div ([
            dcc.Graph(id='summary_pie1', ),
        ],className='col-sm-3'),

    ],className='container-fluid well'),  
    html.Div([  
        
        html.Div([
            html.H3(children='Industries'),  
            html.Div([
                html.H5(
                    children='Job Category (leave blank for all):'),
                dcc.Dropdown(
                    id='position_select3',
                    options=[{'label': ii, 'value': i} for i, ii in zip(db_app.POSITIONS, db_app.POSITION_LABLES)],
                    value='',
                    clearable=True,
            )]),
            html.Div ([
                html.Div(id='summary_industries',className='summary'),
            ]),
        ],className='col-sm-3 container-fluid'),
        html.Div([
            html.Div ([
               dcc.Graph(id='gr_by_sector_counts'),
            ],className=['col-sm-6']),
            html.Div ([
                dcc.Graph(id='gr_by_sector_salary'),
            ],className=['col-sm-6']),
        ],className='col-sm-9 container-fluid'),
    ],className=['col-sm-12 panel']),
    html.Div ([
        
        html.Div([
            html.H3(children='Job Categories'),
                html.Div([
                      html.Div([
                          html.H5(children='Industry (leave blank for all):'),
                          dcc.Dropdown(
                                      id='sector_select3',
                                      options=[{'label': i, 'value': i} for i in db_app.SECTORS]
                      )]),
                      html.Div([
                          html.H5(children='Company (leave blank for all):'),
                          dcc.Dropdown(
                                      id='companies_select3'
                      )]),

                    
                    html.Div ([
                        html.Div(id='summary_categories',className='summary'),
                    ]),
                ]),
        ],className='col-sm-3 container-fluid'),
        html.Div([
            html.Div ([
               dcc.Graph(id='gr_by_job_counts'),
            ],className=['col-sm-6']),
            html.Div ([
                dcc.Graph(id='gr_by_job_salary'),
            ],className=['col-sm-6']),
        ],className='col-sm-9 container-fluid'),
    ],className=['col-sm-12 panel']),
    html.Div([
        html.Div(id='dedug-out',style={'display': 'None'}),
    ],className=['col-sm-12 panel panel-default'])

])



@app.callback(
    Output(component_id='summary_industries', component_property='children'),
    [Input(component_id='position_select3', component_property='value'),
    Input(component_id='inflation_ajust3', component_property='values'),
    Input(component_id='include_benefits3', component_property='values'),
    Input(component_id='include_salary3', component_property='values'),
    Input(component_id='salary_slider3', component_property='value')])
def displaySummaryByIndustry(position, inflation,benefits,salary,salaries):

    df_temp = db_app.df18.copy()
    
    if position!='' and position!=None:
        if position=='chief':
            df_temp=df_temp[df_temp.job_category2=='chief']
        else :
            df_temp=df_temp[df_temp.job_category1==position]

    if df_temp.shape[0]==0:
        return html.Div(children = 'No Results Returned',className= ['alert alert-info'])
    else:

        earn_column = fun.get_earnings_column(inflation, salary, benefits)
        if earn_column=="":
            return html.Div(children = 'No Results Returned',className= ['alert alert-info'])

        if df_temp.shape[0]==0 :
            return html.Div(children = 'No Results Returned',className= ['alert alert-info'])
        
        df_temp = df_temp[df_temp[earn_column]>=salaries[0]]
        if (salaries[1]<600000):
            df_temp = df_temp[df_temp[earn_column]<=salaries[1]]

        if df_temp.shape[0]==0:
                return html.Div(children = 'No Results Returned',className= ['alert alert-info'])


        df_m= df_temp[df_temp._gender_x.astype(str)=='male']
        df_f= df_temp[df_temp._gender_x.astype(str)=='female']

        f_count = df_f.shape[0]
        m_count = df_m.shape[0]
        
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

        return fun.generate_table(temp_df, title = "Industry Summary", display_columns=False)

@app.callback(
    Output(component_id='summary_categories', component_property='children'),
    [Input(component_id='sector_select3', component_property='value'),
    Input(component_id='companies_select3', component_property='value'),
    Input(component_id='inflation_ajust3', component_property='values'),
    Input(component_id='include_benefits3', component_property='values'),
    Input(component_id='include_salary3', component_property='values'),
    Input(component_id='salary_slider3', component_property='value')])
def displaySummaryByCategory(sector,company, inflation,benefits,salary,salaries):
    
    df_temp = db_app.df18.copy()
    df_temp = df_temp[df_temp.job_category1 != 'none']
    
    if (sector != None):
        df_temp = df_temp[df_temp._sector == sector]
        
    else:
        sector = "All Industries"

    if ( company != None):
        df_temp = df_temp[df_temp.employer==company]
    else:
        company = "All Companies"

    if df_temp.shape[0]==0:
        return html.Div(children = 'No Results Returned',className= ['alert alert-info'])
    else:

        earn_column = fun.get_earnings_column(inflation, salary, benefits)
        if earn_column=="":
            return html.Div(children = 'No Results Returned',className= ['alert alert-info'])

        if df_temp.shape[0]==0 :
            return html.Div(children = 'No Results Returned',className= ['alert alert-info'])

        df_temp = df_temp[df_temp[earn_column]>=salaries[0]]
        if (salaries[1]<600000):
            df_temp = df_temp[df_temp[earn_column]<=salaries[1]]

        if df_temp.shape[0]==0:
                return html.Div(children = 'No Results Returned',className= ['alert alert-info'])

        df_temp = pd.DataFrame(df_temp.groupby(['_sector','_gender_x']).agg({'first_name':len, earn_column:np.mean}))
        df_temp.reset_index(inplace=True)

        df_temp.columns=['_sector','_gender_x','first_name','salary_x']
        df_temp = df_temp.sort_values('_sector', ascending = False).reset_index(drop=True)

        df_m= df_temp[df_temp._gender_x.astype(str)=='male']
        df_f= df_temp[df_temp._gender_x.astype(str)=='female']

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

        return fun.generate_table(temp_df, title = "Job Categories Summary", display_columns=False)


###############################################################################
# CALLBACKS: GRAPHS
###############################################################################
@app.callback(
    Output(component_id='summary_pie', component_property='figure'),
    [Input(component_id='inflation_ajust3', component_property='values'),
    Input(component_id='include_benefits3', component_property='values'),
    Input(component_id='include_salary3', component_property='values'),
    Input(component_id='salary_slider3', component_property='value')])
def cbg4_3( inflation, benefits, salary, salaries):

    df_temp = db_app.df18.copy()

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

    df_m= df_temp[df_temp._gender_x.astype(str)=='male']
    df_f= df_temp[df_temp._gender_x.astype(str)=='female']
    ret =  {
            'data': [
                {'values': [ int(df_m.shape[0]), int(df_f.shape[0])], 'type': 'pie', 'hoverinfo':'skip',
                'labels': ['Male','Female'],'textfont':{'size':'120%'},
                'text':['Male: '+ "{:,}".format(df_m.shape[0]),'Female: ' + "{:,}".format(df_f.shape[0])],
                'marker':{'colors':[db_app.COLORS['cmale'],db_app.COLORS['cfemale']]}},
            ],
            'layout': {
                'plot_bgcolor': '#f5f5f5',
                'paper_bgcolor': '#f5f5f5',
                'title': "Counts",
                'font': {
                    # 'color': db_app.COLORS['text'],
                    'size':'120%'},
                'margin':{'t':25,'r':0,'l':0,'b':0},
                'height': 240,
                'legend':{'orientation':"h"},
                'showlegend':False,
            }
        }
    return ret

@app.callback(
    Output(component_id='summary_pie1', component_property='figure'),
    [Input(component_id='inflation_ajust3', component_property='values'),
    Input(component_id='include_benefits3', component_property='values'),
    Input(component_id='include_salary3', component_property='values'),
    Input(component_id='salary_slider3', component_property='value')])
def cbg4_4( inflation, benefits, salary, salaries):

    df_temp = db_app.df18.copy()

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

    df_m= df_temp[df_temp._gender_x.astype(str)=='male']
    df_f= df_temp[df_temp._gender_x.astype(str)=='female']

    m_mean = int(df_m[earn_column].mean())
    f_mean = int(df_f[earn_column].mean())
    return {
            'data': [
                {'values': [ m_mean, f_mean], 'type': 'pie', 'hoverinfo':'skip', 
                'labels': ['',''],'textfont':{'size':'120%'},
                'text':[["$"+ "{:,}".format(m_mean)], "$"+ "{:,}".format(f_mean)],
                'marker':{'colors':[db_app.COLORS['cmale'],db_app.COLORS['cfemale']]}},
            ],
            'layout': {
                'plot_bgcolor': '#f5f5f5',
                'paper_bgcolor': '#f5f5f5',
                'title': "Avg Earnings",
                'font': {
                    'size':'120%'},
                'margin':{'t':25,'r':0,'l':0,'b':0},
                'height': 240,
                'legend':{'orientation':"h"},
                'showlegend':False,
            }
        }


@app.callback(
    Output(component_id='gr_by_sector_counts', component_property='figure'),
    [Input(component_id='position_select3', component_property='value'),
    Input(component_id='inflation_ajust3', component_property='values'),
    Input(component_id='include_benefits3', component_property='values'),
    Input(component_id='include_salary3', component_property='values'),
    Input(component_id='salary_slider3', component_property='value')])
def cbg1_3( position, inflation, benefits, salary, salaries):

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

        df_temp = pd.DataFrame(df_temp.groupby(['_sector','_gender_x']).agg({'first_name':len, earn_column:np.mean}))
        df_temp.reset_index(inplace=True)

        df_temp.columns=['_sector','_gender_x','first_name','salary_x']
        df_temp = df_temp.sort_values('_sector', ascending = False).reset_index(drop=True)

        df_m= df_temp[df_temp._gender_x.astype(str)=='male']
        df_f= df_temp[df_temp._gender_x.astype(str)=='female']
    return fun.format_h_stack_graph_data(df_f,df_m, '_sector', 'first_name','Earnings by Industry', 450 )

@app.callback(
    Output(component_id='gr_by_sector_salary', component_property='figure'),
    [Input(component_id='position_select3', component_property='value'),
    Input(component_id='inflation_ajust3', component_property='values'),
    Input(component_id='include_benefits3', component_property='values'),
    Input(component_id='include_salary3', component_property='values'),
    Input(component_id='salary_slider3', component_property='value')])
def cbg2_3(position, inflation, benefits, salary, salaries):

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

        df_temp = df_temp[df_temp[earn_column]>=salaries[0]]
        if (salaries[1]<600000):
            df_temp = df_temp[df_temp[earn_column]<=salaries[1]]

        if df_temp.shape[0]==0:
                return ""

        df_temp = pd.DataFrame(df_temp.groupby(['_sector','_gender_x']).agg({'first_name':len, earn_column:np.mean}))
        df_temp.reset_index(inplace=True)

        df_temp.columns=['_sector','_gender_x','first_name','salary_x']
        df_temp = df_temp.sort_values('_sector', ascending = False).reset_index(drop=True)

        df_m= df_temp[df_temp._gender_x.astype(str)=='male']
        df_f= df_temp[df_temp._gender_x.astype(str)=='female']

    return fun.format_h_stack_graph_data(df_f,df_m, '_sector', 'salary_x','Earnings by Industry', 450 )

@app.callback(
    Output(component_id='gr_by_job_counts', component_property='figure'),
    [Input(component_id='sector_select3', component_property='value'),
    Input(component_id='companies_select3', component_property='value'),
    Input(component_id='inflation_ajust3', component_property='values'),
    Input(component_id='include_benefits3', component_property='values'),
    Input(component_id='include_salary3', component_property='values'),
    Input(component_id='salary_slider3', component_property='value')])
def cbg1_3( sector, company, inflation, benefits, salary, salaries):

    df_temp = db_app.df18.copy()
    df_temp = df_temp[df_temp.job_category1 != 'none']


    if (sector != None):
        df_temp = df_temp[df_temp._sector == sector]
        # raise ValueError(df_temp.shape, 23)
    else:
        sector = "All Industries"

    if ( company != None):
        df_temp = df_temp[df_temp.employer==company]
    else:
        company = "All Companies"

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

        df_temp = pd.DataFrame(df_temp.groupby(['job_category1','_gender_x']).agg({'first_name':len, earn_column:np.mean}))
        df_temp.reset_index(inplace=True)

        df_temp.columns=['job_category1','_gender_x','first_name','salary_x']
        df_temp = df_temp.sort_values('job_category1', ascending = False).reset_index(drop=True)

        df_m= df_temp[df_temp._gender_x.astype(str)=='male']
        df_f= df_temp[df_temp._gender_x.astype(str)=='female']
    return fun.format_h_stack_graph_data(df_f,df_m, 'job_category1','first_name', '# of Employees by Job Category', 650)

@app.callback(
    Output(component_id='gr_by_job_salary', component_property='figure'),
    [Input(component_id='sector_select3', component_property='value'),
    Input(component_id='companies_select3', component_property='value'),
    Input(component_id='inflation_ajust3', component_property='values'),
    Input(component_id='include_benefits3', component_property='values'),
    Input(component_id='include_salary3', component_property='values'),
    Input(component_id='salary_slider3', component_property='value')])
def cbg1_3( sector, company, inflation, benefits, salary, salaries):

    df_temp = db_app.df18.copy()
    df_temp = df_temp[df_temp.job_category1 != 'none']

    if (sector != None):
        df_temp = df_temp[df_temp._sector == sector]
        # raise ValueError(df_temp.shape, 23)
    else:
        sector = "All Industries"

    if ( company != None):
        df_temp = df_temp[df_temp.employer==company]
    else:
        company = "All Companies"

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


        df_temp = pd.DataFrame(df_temp.groupby(['job_category1','_gender_x']).agg({'first_name':len, earn_column:np.mean}))
        df_temp.reset_index(inplace=True)

        df_temp.columns=['job_category1','_gender_x','first_name','salary_x']
        df_temp = df_temp.sort_values('job_category1', ascending = False).reset_index(drop=True)

        df_m= df_temp[df_temp._gender_x.astype(str)=='male']
        df_f= df_temp[df_temp._gender_x.astype(str)=='female']
    return fun.format_h_stack_graph_data(df_f,df_m, 'job_category1', 'salary_x', 'Earnings by Job Category', 650)    


###############################################################################
# POPULATE COMPANIES BASED ON SECTOR SELECTED
###############################################################################
@app.callback(
    Output(component_id='companies_select3', component_property= 'options'),
    [Input(component_id='sector_select3', component_property='value')])
def call1_3(value):
    temp = db_app.df[db_app.df._sector==value]
    options=[]
    ret1 = temp.employer.unique()
    ret1 = list(ret1)
    ret1.sort()
    for i in ret1:
        options.append({'label': i, 'value': i})
    return options

@app.callback(
    Output(component_id='companies_select3', component_property='value'),
    [Input(component_id='sector_select3', component_property='value')])
def call2_3(value):
    return None




#        