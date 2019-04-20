import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

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


df = db_app.df18.copy()


###############################################################################
# HTML layout
###############################################################################
layout = html.Div(children=[
    html.Div([
        html.Div([
            html.Div([
                html.H5(children='Select Income Range :'),
                dcc.RangeSlider(
                    id = 'salary_slider4',
                    marks={i: {'label': ii, 'style':{'font-size':'150%'}} for i,ii in zip(db_app.EARNINGS,db_app.EARNING_LABLES)},
                    min=0,
                    max=db_app.EARNINGS[-1],
                    step=10000,
                    value=[db_app.EARNINGS[0], db_app.EARNINGS[-1]],
                )],className=['container-fluid'],style={'margin-bottom':'4em', 'margin-top':0}),
                html.Div([dcc.Checklist(
                            id='inflation_ajust4',
                            options=[{'label': i ,'value':i} for i in ['Adjust for Inflation']],
                            values=[],
                )],className=['col-sm-4'] ),
                html.Div([dcc.Checklist(
                            id='include_benefits4',
                            options=[{'label': i ,'value':i} for i in ['Include Benefits']],
                            values=[],
                            
                )],className=['col-sm-4'] ),
                html.Div([dcc.Checklist(
                            id='include_salary4',
                            options=[{'label': i ,'value':i} for i in ['Include Base Salary']],
                            values=['Include Base Salary'],
                            
                )],className=['col-sm-4'] ),
        ],className='col-sm-5'),
        html.Div ([
                html.Div([
                      html.H5(children='Industry:'),
                      dcc.Dropdown(
                                  id='sector_select4',
                                  options=[{'label': i, 'value': i} for i in db_app.SECTORS],
                               #   value='Government of Ontario - Judiciary'
                  )]),
                  html.Div([
                      html.H5(children='Company:'),
                      dcc.Dropdown(
                                  id='companies_select4', 
                                  #value='Ontario Court of Justice'
                  )]),
                  html.Div ([
                      html.Button('Generate Report', id='generate_button', className='btn'),
                  ]),
            ],className='col-sm-3'),
        html.Div([
            # html.Div( id='message_box',className = ['alert alert-info col-sm-12']),
            html.Div([
                html.Div ([
                   dcc.Graph(id='company_pie1', ),
                ], className='col-sm-6'),
                html.Div ([
                    dcc.Graph(id='company_pie2', ),
                ],className='col-sm-6'),
            ],className='container-fluid'),
        ],className=['col-sm-4'])

    ],className='container-fluid well'), 

    html.Div([  
        html.Div([
            html.H2( id = 'company_title'), 
        ],className='col-sm-6'),
        html.Div([
            html.H2("Ratings"),
        ],className='col-sm-6'),
    ],className=['container-fluid']),

    html.Div ([
        html.Div ([
           dcc.Graph(id='company_gr1'),
        ],className='container-fluid'),
        html.H2(""),
        html.Div ([
            dcc.Graph(id='company_by_jobs_graph', ),
        ],className='container-fluid'),
    ],className=['col-sm-6 container-fluid']),



    html.Div([

        html.Div([
            html.Div([
                html.Div ([
                    html.Div(id='company_ratings_summary',className='ratings_summary'),
                ],),
            ],className= ['col-sm-4']),
            html.Div([
                html.Div ([
                    html.Div(id='ratings_all_summary',className='ratings_summary'),
                ],),
            ],className= ['col-sm-8']),
        ],className='container-fluid well'),
    ],className=['col-sm-6 container-fluid']),


    # html.Div(id='intermediate-value4',style={'display': 'block'}),
])


# @app.callback(
#     Output(component_id='generate_button-value4', component_property='n_clicks'),
#     [ Input(component_id='companies_select4', component_property='value'),])
# def company_was_changed(company):
#     return 1

@app.callback(
    Output(component_id='company_title', component_property='children'),
    [ Input(component_id='generate_button', component_property='n_clicks'),],
    [ State(component_id='companies_select4', component_property='value'),])
def update_company(n,company):
    if company == None or company== "":
        return ""
    else:
        return company + " Summary"

# @app.callback(
#     Output(component_id='company_title', component_property='children'),
#     [ Input(component_id='companies_select4', component_property='value'),])
# def update_company(company):
#     if company == None or company== "":
#         return ""


@app.callback(
    Output(component_id='company_by_jobs_graph', component_property='figure'),
    [ Input(component_id='generate_button', component_property='n_clicks'),],
    [State(component_id='companies_select4', component_property='value'),
    State(component_id='inflation_ajust4', component_property='values'),
    State(component_id='include_benefits4', component_property='values'),
    State(component_id='include_salary4', component_property='values'),
    State(component_id='salary_slider4', component_property='value')])
def cbg1_3(n, company, inflation, benefits, salary, salaries):

    if (company == "" or company==None):
        return ""
    df_temp=df[df.employer==company]

    if df_temp.shape[0]==0:
        return {}
    else:
        earn_column = fun.get_earnings_column(inflation, salary, benefits)
        if earn_column=="":
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

        dd = pd.merge(df_f, df_m, how='outer', left_on='job_category1', right_on='job_category1')
        dd.fillna(0, inplace=True)

        dd['female_per'] = fun.get_f_count_number(dd.first_name_x, dd.first_name_y)
        dd['male_per'] = fun.get_m_count_number(dd.first_name_x, dd.first_name_y)
        # raise ValueError(dd.columns, 23)

        return {
            'data': [
                {'y': dd.job_category1, 'x': dd.male_per, 'type': 'bar', 'name': '','textfont':{'size':'120%'}, 'orientation':'h',
                'textposition':'inside','hoverinfo':'skip',
                'insidetextfont':{'size':'120%'}, 
                'text': "Male: " + dd.first_name_y.astype(int).astype(str) +  " ("+ dd.male_per.astype(str) + "%)",
                'marker':{'color':db_app.COLORS['cmale']}},

                {'y': dd.job_category1, 'x': dd.female_per, 'type': 'bar', 'name': '','textfont':{'size':'120%'}, 'orientation':'h',
                'textposition':'inside', 'hoverinfo':'skip',
                'insidetextfont':{'size':'120%'}, 
                'text': "Female: " + dd.first_name_x.astype(int).astype(str) +  " ("+dd.female_per.astype(str) + "%)",
                'marker':{'color':db_app.COLORS['cfemale']}},
            ],
            'layout': {
                'barmode':'stack',
                'title': '% of Female vs % of Male by Job Category',
                'plot_bgcolor': db_app.COLORS['background'],
                'paper_bgcolor': db_app.COLORS['background'],
                'font': {
                    'color': db_app.COLORS['text'],
                    'size':'120%'},
                'margin':{'t':'1em','r':40,'l':(24*7),'b':50},
                # 'height': height,
                'legend':{'orientation':"h"},
                'showlegend':False,
                'xaxis':dict(showticklabels=False,gridcolor='white', gridwidth=0.5)
            }
        }
    # return fun.format_h_stack_graph_data(df_f,df_m, 'job_category1','first_name', '# of Employees by Job Category', 650)

@app.callback(
    Output(component_id='company_pie1', component_property='figure'),
    [ Input(component_id='generate_button', component_property='n_clicks'),],
    [State(component_id='companies_select4', component_property='value'),
    State(component_id='inflation_ajust4', component_property='values'),
    State(component_id='include_benefits4', component_property='values'),
    State(component_id='include_salary4', component_property='values'),
    State(component_id='salary_slider4', component_property='value')])
def company_pie1_generate(n, company, inflation, benefits, salary, salaries):
    if (company == "" or company==None):
        return ""
    df_temp=df[df.employer==company]

    if df_temp.shape[0]==0:
        return {}
    else:
        earn_column = fun.get_earnings_column(inflation, salary, benefits)
        if earn_column=="":
            return {}

        if df_temp.shape[0]==0 :
            return {}

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
                    'labels': ['',''],'textfont':{'size':'120%'},'text':['Male: '+ "{:,}".format(df_m.shape[0]),'Female: ' + "{:,}".format(df_f.shape[0])],
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
                    'height': 200,
                    'legend':{'orientation':"h"},
                    'showlegend':False,
                }
            }
        return ret

@app.callback(
    Output(component_id='company_pie2', component_property='figure'),
    [ Input(component_id='generate_button', component_property='n_clicks'),],
    [State(component_id='companies_select4', component_property='value'),
    State(component_id='inflation_ajust4', component_property='values'),
    State(component_id='include_benefits4', component_property='values'),
    State(component_id='include_salary4', component_property='values'),
    State(component_id='salary_slider4', component_property='value')])
def company_pie2_generate(n, company, inflation, benefits, salary, salaries):
    if (company == "" or company==None):
        return ""
    df_temp=df[df.employer==company]

    if df_temp.shape[0]==0:
        return {}
    else:
        earn_column = fun.get_earnings_column(inflation, salary, benefits)
        if earn_column=="":
            return {}

        if df_temp.shape[0]==0 :
            return {}

        df_temp = df_temp[df_temp[earn_column]>=salaries[0]]
        if (salaries[1]<600000):
            df_temp = df_temp[df_temp[earn_column]<=salaries[1]]

        if df_temp.shape[0]==0:
                return ""

        df_m= df_temp[df_temp._gender_x.astype(str)=='male']
        df_f= df_temp[df_temp._gender_x.astype(str)=='female']
        
        m_mean = 0
        if df_m.shape[0]>0:
            m_mean = int(df_m[earn_column].mean())
        f_mean = 0
        if df_f.shape[0]>0:
            f_mean = int(df_f[earn_column].mean())

        ret =  {
                'data': [
                    {'values': [ m_mean, f_mean], 'type': 'pie', 'hoverinfo':'skip',
                    'labels': ['',''],'textfont':{'size':'120%'},'text':[["$"+ "{:,}".format(m_mean)], "$"+ "{:,}".format(f_mean)],
                    'marker':{'colors':[db_app.COLORS['cmale'],db_app.COLORS['cfemale']]}},
                ],
                'layout': {
                    'plot_bgcolor': '#f5f5f5',
                    'paper_bgcolor': '#f5f5f5',
                    'title': "Avg Earnings",
                    'font': {
                        # 'color': db_app.COLORS['text'],
                        'size':'120%'},
                    'margin':{'t':25,'r':0,'l':0,'b':0},
                    'height': 200,
                    'legend':{'orientation':"h"},
                    'showlegend':False,
                    'textposition':'outside',
                }
            }
        return ret

@app.callback(
    Output(component_id='company_gr1', component_property='figure'),
    [ Input(component_id='generate_button', component_property='n_clicks'),],
    [State(component_id='companies_select4', component_property='value'),
    State(component_id='inflation_ajust4', component_property='values'),
    State(component_id='include_benefits4', component_property='values'),
    State(component_id='include_salary4', component_property='values'),
    State(component_id='salary_slider4', component_property='value')])
def company_summary1_generate(n, company, inflation, benefits, salary, salaries):
    if (company == "" or company==None):
        return ""
    df_temp=df[df.employer==company]

    if df_temp.shape[0]==0:
        return ""
    else:
        earn_column = fun.get_earnings_column(inflation, salary, benefits)
        if earn_column=="":
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

        df_temp = pd.merge(df_temp[df_temp._gender_x=='female'],df_temp[df_temp._gender_x=='male'], how='outer',left_on='quantiles', right_on='quantiles' )

        df_temp.salary_min_x.fillna(1000000, inplace=True)
        df_temp.salary_max_x.fillna(0, inplace=True)


        # df_temp['range'] = df_temp.apply(lambda x: "$" + str(min([x.salary_min_x,x.salary_min_y]))[:3] + "K - $" + str(max([x.salary_max_x,x.salary_max_y]))[:3]+"K", axis=1)
        df_temp['range'] = df_temp.apply(lambda x: "$" + "{:,}".format(min([x.salary_min_x,x.salary_min_y])) + " - $" + "{:,}".format(max([x.salary_max_x,x.salary_max_y])), axis=1)
        # group one more time, because sometimes we end up with multile ranges of the same values 
        # bug in pandas
        df_temp = df_temp.groupby(['range'])['first_name_x','first_name_y'].sum()
        df_temp.reset_index(inplace=True)

        df_temp.sort_values(by=['range'], ascending = False, inplace=True)

        # raise ValueError(df_temp[['quantiles','salary_min_x','salary_min_y', 'range']], 23)

        df_temp.fillna(0, inplace=True)
        
        df_temp['female_per'] = fun.get_f_count_number(df_temp.first_name_x, df_temp.first_name_y)
        df_temp['male_per'] = fun.get_m_count_number(df_temp.first_name_x, df_temp.first_name_y)

    return {
            'data': [
                {'y': df_temp.range, 'x': df_temp.male_per, 'type': 'bar', 'name': '','textfont':{'size':'120%'}, 'orientation':'h',
                'textposition':'inside', 'hoverinfo':'skip',
                'insidetextfont':{'size':'120%'}, 
                'text': "Male: " + df_temp.first_name_y.astype(int).astype(str) +  " ("+ df_temp.male_per.astype(str) + "%)",
                'marker':{'color':db_app.COLORS['cmale']}},

                {'y': df_temp.range, 'x': df_temp.female_per, 'type': 'bar', 'name': '','textfont':{'size':'120%'}, 'orientation':'h',
                'textposition':'inside', 'hoverinfo':'skip',
                'insidetextfont':{'size':'120%'}, 
                'text': "Female: " + df_temp.first_name_x.astype(int).astype(str) +  " ("+df_temp.female_per.astype(str) + "%)",
                'marker':{'color':db_app.COLORS['cfemale']}},
            ],
            'layout': {
                'barmode':'stack',
                'title': '% of Female vs % of Male by Earning Ranges',
                'plot_bgcolor': db_app.COLORS['background'],
                'paper_bgcolor': db_app.COLORS['background'],
                'font': {
                    'color': db_app.COLORS['text'],
                    'size':'120%'},
                'margin':{'t':'1em','r':40,'l':(24*7),'b':50},
                # 'height': height,
                'legend':{'orientation':"h"},
                'showlegend':False,
                'xaxis':dict(showticklabels=False,gridcolor='white', gridwidth=0.5)
            }
        }


@app.callback(
    Output(component_id='ratings_all_summary', component_property='children'),
    [Input(component_id='generate_button', component_property='n_clicks'),],
    [State(component_id='companies_select4', component_property='value'),
    State(component_id='sector_select4', component_property='value')])
def ratings_all_summary(n, company, sector):

    if (company == "" or company==None or sector== "" or sector == None):
        return ""
    df_temp=df[df._sector==sector]

    if df_temp.shape[0]==0:
        return ""
    else:
        # 
        df_temp = pd.DataFrame(df_temp.groupby(['employer']).agg({'avg_indeed_score':np.max,'num_reviews':np.max
            ,'culture':np.max, 'work_life':np.max}))
        df_temp.reset_index(inplace=True)
        df_temp.sort_values(by=['avg_indeed_score','num_reviews'], ascending=False, inplace=True)
        df_temp.index=range(1,df_temp.shape[0]+1)
        df_temp.reset_index(inplace=True)

        df_temp.columns = ['Rank','Company','Avg Score', '# of Reviews', 'Culture','Work/Life Balance']

        ranks = df_temp[df_temp.Company==company].Rank.tolist()
        my_rank = 0
        if df_temp.shape[0]>0:
            my_rank = ranks[0] -1
        else:
            return ""

        highlight_row = my_rank
        company_count = df_temp.shape[0]

        if my_rank > 9:
            df_temp = df_temp[:9].append(df_temp.iloc[my_rank])
            highlight_row = 9
        else:
            df_temp = df_temp[:10]

        # raise ValueError(my_rank, 23)

        return fun.generate_table(df_temp, title = "Industry Ranking ("+str(company_count)+" companies ranked)", display_columns=True, highlight_row =highlight_row)
            # dtypes = ["","num","num","per","num","num","per"])


@app.callback(
    Output(component_id='company_ratings_summary', component_property='children'),
    [Input(component_id='generate_button', component_property='n_clicks'),],
    [State(component_id='companies_select4', component_property='value'),])
def company_ratings_summary_generate(n, company):
    if (company == "" or company==None):
        return ""
    df_temp=df[df.employer==company]

    if df_temp.shape[0]==0:
        return ""
    else:

        if df_temp.got_indeed_review.max()<1:
            return "No Reviews Posted"

        temp = []
        if df_temp.num_reviews.max() > 0:
            temp.append(["# of Reviews", "{:,}".format(df_temp.num_reviews.max())])
        if df_temp.avg_indeed_score.max() >0:
            temp.append(["Overall Score", "{:,}".format(df_temp.avg_indeed_score.max())])
        if df_temp.num_employees.max() == df_temp.num_employees.max():
            temp.append(["# of Employees", df_temp.num_employees.max()])
        if df_temp.ceo.max() > 0:
            temp.append(["CEO Approval", "{:,}".format(int(df_temp.ceo.max()))+"%"])
        if df_temp.work_life.max() > 0:
            temp.append(["Work/Life Balance", "{:,}".format(df_temp.work_life.max())])
        if df_temp.salary.max() > 0:
            temp.append(["Salary/Benefits", "{:,}".format(df_temp.salary.max())])
        if df_temp.job_security.max() > 0:
            temp.append(["Job Security/Advancement", "{:,}".format(df_temp.job_security.max())])
        if df_temp.management.max() > 0:
            temp.append(["Management", "{:,}".format(df_temp.management.max())])
        if df_temp.culture.max() > 0:
            temp.append(["Culture", "{:,}".format(df_temp.culture.max())])
        if len(str(df_temp.pay_details.max()).strip()) > 3:
            temp.append(["Earnings Details", df_temp.pay_details.max()])
        if len(str(df_temp.revinew.max()).strip()) > 3:
            temp.append(["Revinew", df_temp.revinew.max()])

        temp_df = pd.DataFrame(temp)
        if(temp_df.shape[0]==0):
            return "No Reviews for " + company

        return fun.generate_table(temp_df, title = "Ranking Summary", display_columns=False, highlight_row =1)


@app.callback(
    Output('message_box', 'children'),
    [ Input(component_id='generate_button', component_property='n_clicks'),],
    [State(component_id='companies_select4', component_property='value')])

def generate_company_summary(clicks, company,):
    # raise ValueError(company, 23)
    if (company == "" or company==None):
        return "Company Must be Selected. "
    else:
        return "Select company and press Generate."



###############################################################################
# POPULATE COMPANIES BASED ON SECTOR SELECTED
###############################################################################
@app.callback(
    Output(component_id='companies_select4', component_property= 'options'),
    [Input(component_id='sector_select4', component_property='value')])
def call1_3(value):
    temp = df[df._sector==value]
    options=[]
    ret1 = temp.employer.unique()
    ret1 = list(ret1)
    ret1.sort()
    for i in ret1:
        options.append({'label': i, 'value': i})
    return options

# @app.callback(
#     Output(component_id='companies_select4', component_property='value'),
#     [Input(component_id='sector_select4', component_property='value')])
# def call2_3(value):
#     return 'None'




#        