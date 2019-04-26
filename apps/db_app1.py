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
                    id = 'salary_slider',
                    marks={i: {'label': ii, 'style':{'font-size':'150%'}} for i,ii in zip(db_app.EARNINGS,db_app.EARNING_LABLES)},
                    min=0,
                    max=db_app.EARNINGS[-1],
                    step=10000,
                    value=[db_app.EARNINGS[0], db_app.EARNINGS[-1]],
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
                
        ],className='col-sm-5'),
        html.Div([
          html.Div([
                  html.Div([
                      html.H5(children='Sector (leave blank for all):'),
                      dcc.Dropdown(
                                  id='sector_select',
                                  options=[{'label': i, 'value': i} for i in db_app.SECTORS],
                                  value = None
                  )]),
                  html.Div([
                      html.H5(children='Employer (leave blank for all):'),
                      dcc.Dropdown(
                                  id='companies_select'
                  )]),

             ],className='container-fluid'),
        ],className='col-sm-3'),
        html.Div([
            html.Div([
                html.H5(children='Role (leave blank for all):'),
                dcc.Dropdown(
                    id='position_select',
                    options=[{'label': ii, 'value': i} for i, ii in zip(db_app.POSITIONS, db_app.POSITION_LABLES)],
                    value='',
                    clearable=True,),
                html.H5(""),
                html.Div([dcc.Checklist(
                            id='inflation_ajust',
                            options=[{'label': i ,'value':i} for i in ['Adjust for Inflation']],
                            values=[],
                )],className="" ),
                html.Div([dcc.Checklist(
                            id='include_benefits',
                            options=[{'label': i ,'value':i} for i in ['Benefits']],
                            values=[],
                            
                )],className="" ),
                html.Div([dcc.Checklist(
                            id='include_salary',
                            options=[{'label': i ,'value':i} for i in ['Salary']],
                            values=['Salary'],
                )],className="" ),

                ]),
        ],className='col-sm-3'),
    ],className='container-fluid well'),


    html.Div([
        html.Div ([
           dcc.Graph(id='graph_counts',className=''),
        ],className='container-fluid'),

        html.Div ([
            dcc.Graph(id='graph_salaries',className=''),
        ],className='container-fluid'),
    ],className='col-sm-6 container-fluid'),

    html.Div([
        html.Div([
            html.Div ([
                dcc.Graph(id='stacked_area',className=''),
                ],className='col-sm-6 container-fluid', style={'margin':0}),
            html.Div ([
                dcc.Graph(id='stacked_area1',className=''),
                ],className='col-sm-6 container-fluid', style={'margin':0}),
        ],className='container-fluid'),
        html.Div(id='sector_avg_box', className='summary'),
    ],className='col-sm-6 container-fluid'),

    html.Div(id='intermediate-value',style={'display': 'None'}),
])


###############################################################################
# CALLBACKS
###############################################################################

###############################################################################
# List of companies for this sector 
###############################################################################
@app.callback(
    Output(component_id='companies_select', component_property= 'options'),
    [Input(component_id='sector_select', component_property='value')])
def call1(value):
    return fun.get_companies_for_sector(value,db_app.df)

@app.callback(
    Output(component_id='companies_select', component_property='value'),
    [Input(component_id='sector_select', component_property='value')])
def call2(value):
    return None


###############################################################################
# List of roles for this sector 
###############################################################################
@app.callback(
    Output(component_id='position_select', component_property= 'options'),
    [Input(component_id='sector_select', component_property='value')])
def call1(value):
    return fun.get_roles(value, db_app.df)

@app.callback(
    Output(component_id='position_select', component_property= 'value'),
    [Input(component_id='sector_select', component_property='value'),
    Input(component_id='companies_select', component_property='value')])
def call11(value, valu):
    return None


#################################################################################
# DATA PREPARATION
# get records based on selected parameters and dump them into intermediate-value
# text field, from there those records will be used to create graphs on this tab
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
def clean_data(sector,years, company, position, inflation, benefits, salary, salaries):

    df_temp = db_app.df.copy()

    if position!='' and position!= None:
        if position=='chief':
            df_temp=df_temp[df_temp.job_category2=='chief']
        else :
            df_temp=df_temp[df_temp.job_category1==position]
        
    if (sector != None):
        df_temp = df_temp[df_temp._sector == sector]
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

        df_temp =  df_temp[df_temp.c_year >= int(years[0])]
        df_temp =  df_temp[df_temp.c_year <= int(years[1])]

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

#################################################################################
# SECTOR AVG are displaied at the bottom of the page.
# They are not dependant on selection of sector or the company, so not updated 
# too often.
#################################################################################
@app.callback(
    Output(component_id='sector_avg_box', component_property='children'),
    [Input(component_id='inflation_ajust', component_property='values'),
    Input(component_id='include_benefits', component_property='values'),
    Input(component_id='include_salary', component_property='values'),
    Input(component_id='salary_slider', component_property='value')])
def displaySectorSummary(inflation, benefits, salary, salaries):

    df_temp = db_app.df[db_app.df.c_year==db_app.CURRENT_YEAR]

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

    df_temp = pd.DataFrame(df_temp.groupby(['_gender_x','_sector']).agg({'first_name':len, earn_column:np.mean}))
    df_temp.reset_index(inplace=True)
    df_m= df_temp[df_temp._gender_x.astype(str)=='male']
    df_f= df_temp[df_temp._gender_x.astype(str)=='female']
    dd = pd.merge(df_m,df_f, how='outer', left_on='_sector', right_on="_sector")
    dd.drop(columns=['_gender_x_x','_gender_x_y'],inplace=True)
    dd.columns = ['_sector','m_count','m_salary','f_count','f_salary']

    dd['per_female'] = fun.get_f_count_number(dd.f_count, dd.m_count)

    dd['per_female_salary'] = fun.get_f_count_number(dd.f_salary, dd.m_salary)
    dd.fillna(0, inplace=True)

    dd['difference'] = dd.apply(lambda x: x.f_salary - x.m_salary, axis = 1)

    dd = dd.reindex(columns=['_sector','m_count','f_count','per_female','m_salary','f_salary', 'difference'])
    
    dd.columns = ['Sector','Total (men)','Total (women)', 'Percent (women)','Average salary (men)','Average salary (women)', 'Difference']

    return fun.generate_table(dd, title='Averages by Sector for '+ str(db_app.CURRENT_YEAR),  
        dtypes = ["","num","num","per","dol","dol","dol",],col_to_highlight_negatives=[6],
        col_to_highlight_negatives_per=[3])



###############################################################################
# CALLBACKS: GRAPHS
###############################################################################


###############################################################################
# Small area graph at the top of the page, kind of summary view for sector 
###############################################################################
@app.callback(
    Output(component_id='stacked_area', component_property='figure'),
    [Input(component_id='sector_select', component_property='value'),
    Input(component_id='year_slider', component_property='value'), 
    Input(component_id='position_select', component_property='value'),
    Input(component_id='inflation_ajust', component_property='values'),
    Input(component_id='include_benefits', component_property='values'),
    Input(component_id='include_salary', component_property='values'),
    Input(component_id='salary_slider', component_property='value')])
def populate_sack_1(sector,years, position, inflation, benefits, salary, salaries):

    df_temp = db_app.df.copy()

    if position!='' and position!= None:
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
        return fun.get_default_graph()
    else:

        earn_column = fun.get_earnings_column(inflation, salary, benefits)

        if earn_column=="":
            return fun.get_default_graph()

        df_temp =  df_temp[df_temp.c_year >= int(years[0])]
        df_temp =  df_temp[df_temp.c_year <= int(years[1])]

        if df_temp.shape[0]==0 :
            return fun.get_default_graph()

        df_temp = df_temp[df_temp[earn_column]>=salaries[0]]
        if (salaries[1]<600000):
            df_temp = df_temp[df_temp[earn_column]<=salaries[1]]

        if df_temp.shape[0]==0:
                return fun.get_default_graph()

        df_temp = pd.DataFrame(df_temp.groupby(['c_year','_gender_x']).agg({'first_name':len}))
        df_temp.reset_index(inplace=True)

        df_temp.columns=['c_year','_gender_x','first_name']

        df_m= df_temp[df_temp._gender_x.astype(str)=='male']
        df_f= df_temp[df_temp._gender_x.astype(str)=='female']

        return  {
                'data': [
                    {'x': df_m.c_year, 'y': df_m.first_name,  'name': 'Men','stackgroup':'one','fillcolor':db_app.COLORS['cmale']},
                    {'x': df_f.c_year, 'y': df_f.first_name,  'name': 'Women','stackgroup':'one','fillcolor':db_app.COLORS['cfemale']},
                ],
                'layout' : {
                    'title':'Sector totals',   
                    'margin':{'t':30,'r':20,'l':50,'b':50},
                    'height': 300,
                    'showlegend':True,
                    'legend':{'orientation':"h"},
                        'xaxis':dict(
                                type='category',
                            ),
                        'yaxis':dict(
                                title = 'Men vs Women',
                                type='linear', showticklabels=False,gridcolor='black', gridwidth=0.2, hoverformat = ',2f'
                            )
                        }
                }

###############################################################################
# Small area graph at the top of the page, kind of summary view for company 
###############################################################################
@app.callback(
    Output(component_id='stacked_area1', component_property='figure'),
    [Input('intermediate-value', 'children')])
def populate_sack_2(value):

    if value == "":
        return fun.get_default_graph()

    datasets = json.loads(value)

    df_m= pd.read_json(datasets['df_m'], orient='split')
    df_f= pd.read_json(datasets['df_f'], orient='split')

    return  {
            'data': [
                {'x': df_m.c_year, 'y': df_m.first_name,  'name': 'Men','stackgroup':'one','fillcolor':db_app.COLORS['cmale']},
                {'x': df_f.c_year, 'y': df_f.first_name,  'name': 'Women','stackgroup':'one','fillcolor':db_app.COLORS['cfemale']},
            ],
            'layout' : {
                'title':'Employer Totals',   
                'margin':{'t':30,'r':20,'l':50,'b':50},
                'height': 300,
                'showlegend':True,
                'legend':{'orientation':"h"},
                    'xaxis':dict(
                            type='category',
                        ),
                    'yaxis':dict(
                            title = 'Men vs Women',
                            type='linear', showticklabels=False,gridcolor='black', gridwidth=0.2, hoverformat = ',2f'
                        )
                    }
            }


###############################################################################
# Graph representation of female vs male counts by year
###############################################################################
@app.callback(
    Output(component_id='graph_counts', component_property='figure'),
    [Input('intermediate-value', 'children')])
def call3(value):
    if value == "":
        return fun.get_default_graph()

    datasets = json.loads(value)

    df_m= pd.read_json(datasets['df_m'], orient='split')
    df_f= pd.read_json(datasets['df_f'], orient='split')

    return {
            'data': [
                {'x': df_m.c_year, 'y': df_m.first_name, 'type': 'bar', 'name': 'Men','textposition':'inside',
                'insidetextfont':{'size':'120%'},
                'text': fun.get_m_count(df_f.first_name, df_m.first_name), 
                'marker':{'color':db_app.COLORS['cmale']}},
                {'x': df_f.c_year, 'y': df_f.first_name, 'type': 'bar', 'name': 'Women','textposition':'inside', 
                'insidetextfont':{'size':'120%'},
                'text': fun.get_f_count(df_f.first_name, df_m.first_name), 
                'marker':{'color':db_app.COLORS['cfemale']}},
            ],
            'layout': {
                'title':'Total Employees on Sunshine List',
                'plot_bgcolor': db_app.COLORS['background'],
                'paper_bgcolor': db_app.COLORS['background'],
                'font': {
                    'color': db_app.COLORS['text'],
                    'size':'120%'},
                'xaxis':dict(tickvals = db_app.YEARS, 
                    ticktext = db_app.YEARS),
                'yaxis':dict(title = '',gridcolor='white', gridwidth=0.5, hoverformat = ',2f', tickformat = ',2f')
            }
        }


###############################################################################
# Graph representation of female vs male earnings by year
###############################################################################
@app.callback(
    Output(component_id='graph_salaries', component_property='figure'),
    [Input('intermediate-value', 'children')])
def call4(value):
    if value == "":
        return fun.get_default_graph()

    datasets = json.loads(value)

    df_m= pd.read_json(datasets['df_m'], orient='split')
    df_f= pd.read_json(datasets['df_f'], orient='split')

    y_min = fun.get_min_plus_5(df_m.salary_x, df_f.salary_x)
    y_max = max([df_m.salary_x.max(),df_f.salary_x.max()])
    return {
            'data': [
                {'x': df_m.c_year, 'y': df_m.salary_x.astype(int), 'type': 'bar', 'name': 'Men',
                'marker':{'color':db_app.COLORS['cmale']}},
                {'x': df_f.c_year, 'y': df_f.salary_x.astype(int), 'type': 'bar', 'name': 'Women',
                'marker':{'color':db_app.COLORS['cfemale']}},
            ],
            'layout':
            {
                'title':'Average Salaries',
                'plot_bgcolor': db_app.COLORS['background'],
                'paper_bgcolor': db_app.COLORS['background'],
                
                'font': {
                    'color': db_app.COLORS['text'],
                    'size':'120%'},
                'xaxis':dict(tickvals = db_app.YEARS, 
                    ticktext = db_app.YEARS),
                'yaxis':dict(title = '', gridcolor='white', gridwidth=0.5, hoverformat = '$,2f', range=[y_min, y_max], tickformat = '$,2f')
            # range: [-0.5, 23.5]),

            }
        }
