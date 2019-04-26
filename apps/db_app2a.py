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
                    value=[db_app.EARNINGS[0], db_app.EARNINGS[-1]],
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
                  # html.Div([
                      html.H5(children='Sector I:'),
                      dcc.Dropdown(
                                  id='sector_select2a',
                                  clearable=True,
                                  options=[{'label': i, 'value': i} for i in db_app.SECTORS],
                                  # value = 'Universities'
                  )]),
                  html.Div([
                      html.H5(children='Employer I:'),                      
                      dcc.Dropdown(
                                  id='companies_select_1',
                                  clearable=True,
                                  # value = 'Trent University'
                  )]),
                  

            # ],className=['container-fluid']),
        ],className='col-sm-4'),
        html.Div([
          # html.Div([
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
             # ],className='container-fluid'),
        ],className='col-sm-4'),

    ],className='container-fluid well'),  

    html.Div([       
            # html.Div([
                html.H2(id = 'selecttion_1a_title'),
                html.Div ([
                    html.Div(id='selecttion_1_summary',className='summary'),
                ],className='container-fluid'),
                html.Div ([
                    dcc.Graph(id='dist_graph1a'),
                ],className='container-fluid'),
                html.H2(id='selection_1b_title'), 
                html.Div ([
                    html.Div(id='dist_summary1a',className='summary'),
                ],className='container-fluid'),
            # ],className="col-sm-12 container-fluid"),
        ],className=['col-sm-6']),

    html.Div([
            # html.Div([
                html.H2(id = 'selecttion_2a_title'),
                html.Div ([
                    html.Div(id='selecttion_2_summary',className='summary'),
                ],className='container-fluid'),
                html.Div ([
                    dcc.Graph(id='dist_graph2a'),
                ],className='container-fluid'),
                html.H2(id='selection_2b_title'), 
                html.Div ([
                    html.Div(id='dist_summary2a',className='summary'),
                ],className='container-fluid'),
            # ],className="container-fluid"),

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
    return create_dist_graph(sector, company, position, inflation, benefits, salary, salaries)

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
    return create_dist_graph(sector, company, position, inflation, benefits, salary, salaries)

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
    return create_dist_summary( sector, company, position, inflation, benefits, salary, salaries)

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
    return create_dist_summary( sector, company, position, inflation, benefits, salary, salaries)


###############################################################################
# SUMMARY BOX - for selected sector
# takes into account earnings columns and position
###############################################################################
@app.callback(
    Output(component_id='selecttion_1_summary', component_property='children'),
    [Input(component_id='sector_select2a', component_property='value'),
    Input(component_id='companies_select_1', component_property='value'),
    Input(component_id='position_select2a', component_property='value'),
    Input(component_id='inflation_ajust2a', component_property='values'),
    Input(component_id='include_benefits2a', component_property='values'),
    Input(component_id='include_salary2a', component_property='values'),
    Input(component_id='salary_slider2a', component_property='value')])
def sb2_adjust(sector, company, position, inflation, benefits, salary, salaries):
    return one_line_summary(sector, company, position, inflation, benefits, salary, salaries)

###############################################################################
# SUMMARY BOX - for selected sector
# takes into account earnings columns and position
###############################################################################
@app.callback(
    Output(component_id='selecttion_2_summary', component_property='children'),
    [Input(component_id='sector_select2b', component_property='value'),
    Input(component_id='companies_select_2', component_property='value'),
    Input(component_id='position_select2a', component_property='value'),
    Input(component_id='inflation_ajust2a', component_property='values'),
    Input(component_id='include_benefits2a', component_property='values'),
    Input(component_id='include_salary2a', component_property='values'),
    Input(component_id='salary_slider2a', component_property='value')])
def sb2_adjust(sector, company, position, inflation, benefits, salary, salaries):
    return one_line_summary(sector, company, position, inflation, benefits, salary, salaries)

###############################################################################
# Returns first subtitle or an information box - selection 1
###############################################################################
@app.callback(
    Output(component_id='selecttion_1a_title', component_property='children'),
    [Input(component_id='sector_select2a', component_property='value'),
    Input(component_id='companies_select_1', component_property='value')])
def cbg2(sector, company1):
    
    if sector == None:
        return ""
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
        return ""
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



##############################################################################
# Returns summary table for the distribution graphs (tab 2)
##############################################################################
def create_dist_summary( sector, company, position, inflation, benefits, salary, salaries):
    if (sector==None):
        return ""

    df_temp = db_app.df18[db_app.df18._sector==sector].copy()

    if (company != None):
        df_temp = df_temp[df_temp.employer==company]

    if df_temp.shape[0]==0:
        return ""

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

        b_num = 4
        if df_temp.shape[0]<10:
            b_num = df_temp.shape[0]//3

        df_temp['quantiles']=1
        try:
            df_temp['quantiles']=pd.qcut(df_temp.salary_x.rank(method='first'), b_num)
        except:
            pass

        f = df_temp[df_temp._gender_x=='female']
        m = df_temp[df_temp._gender_x=='male']

        additional = pd.DataFrame([["Totals",f.shape[0],m.shape[0],100,f.salary_x.mean(),m.salary_x.mean(),0]])

        df_temp = pd.DataFrame(df_temp.groupby(['_gender_x','quantiles']).agg({'first_name':len, 'salary_x':[np.mean,np.min,np.max], }))
        df_temp.reset_index(inplace=True)

        df_temp.columns=['_gender_x','quantiles','first_name','salary_x', 'salary_min', 'salary_max']

        df_temp = pd.merge(df_temp[df_temp._gender_x=='female'],df_temp[df_temp._gender_x=='male'], how='outer',left_on='quantiles', right_on='quantiles' )
        
        df_temp['range'] = [i for i in range(1,df_temp.shape[0]+1)]
        df_temp = df_temp[['range','first_name_x','first_name_y','salary_x_x','salary_x_y']]
        df_temp.fillna(0, inplace=True)
        if df_temp.shape[0]==0:
                return "" 

        df_temp['per_female'] = fun.get_f_count_number(df_temp.first_name_x, df_temp.first_name_y)
        df_temp['difference'] = df_temp.apply(lambda x: x.salary_x_x - x.salary_x_y, axis = 1)

        df_temp = df_temp[['range','first_name_x','first_name_y','per_female','salary_x_x','salary_x_y', 'difference']]
       

        additional.columns=df_temp.columns
        additional['per_female'] = fun.get_f_count_number(additional.first_name_x, additional.first_name_y)
        additional['difference'] = additional.apply(lambda x: x.salary_x_x - x.salary_x_y, axis = 1)

        df_temp = pd.concat([df_temp,additional], axis=0)


        df_temp.columns = ['Quartile','Total (women)','Total (men)', 'Percent (women)','Average salary (woman)','Average salary (man)', 'Difference']

    return fun.generate_table(df_temp, title = "" , display_columns=True, 
        dtypes = ["","num","num","per","dol","dol","dol"], col_to_highlight_negatives=[6],
        col_to_highlight_negatives_per=[3])


##############################################################################
# Distribution graph 
##############################################################################
def create_dist_graph(sector, company, position, inflation, benefits, salary, salaries):
    if (sector==None):
        return fun.get_default_graph()

    df_temp = db_app.df18[db_app.df18._sector==sector].copy()

    if (company != None):
        df_temp = df_temp[df_temp.employer==company]

    if df_temp.shape[0]==0:
        return fun.get_default_graph()

    if position!='' and position!=None:
        if position=='chief':
            df_temp=df_temp[df_temp.job_category2=='chief']
        else :
            df_temp=df_temp[df_temp.job_category1==position]

    if df_temp.shape[0]==0:
        return fun.get_default_graph()
    else:

        earn_column = fun.get_earnings_column(inflation, salary, benefits)
        if earn_column=="":
            return fun.get_default_graph()

        if df_temp.shape[0]==0 :
            return fun.get_default_graph()

        df_temp = df_temp[df_temp[earn_column]>=salaries[0]]
        if (salaries[1]<600000):
            df_temp = df_temp[df_temp[earn_column]<=salaries[1]]

        if df_temp.shape[0]==0:
            return fun.get_default_graph()

        df_temp = df_temp[['_gender_x','first_name',earn_column]]
        df_temp.columns=['_gender_x','first_name','salary_x']

        df_m= df_temp[df_temp._gender_x.astype(str)=='male']
        df_f= df_temp[df_temp._gender_x.astype(str)=='female']

    return  fun.format_dist_graph_data(df_f, df_m, sector)

##############################################################################
# One line summary for the selection + top 10 employers
##############################################################################
def one_line_summary(sector, company, position, inflation, benefits, salary, salaries):
    err = html.Div(children = 'Select Sector and Company',className= ['alert alert-info'])
    if (sector==None):
        return err

    df_temp = db_app.df18[db_app.df18._sector==sector].copy()

    if (company != None):
        df_temp = df_temp[df_temp.employer==company]

    if df_temp.shape[0]==0:
        return err

    if position!='' and position!=None:
        if position=='chief':
            df_temp=df_temp[df_temp.job_category2=='chief']
        else :
            df_temp=df_temp[df_temp.job_category1==position]

    if df_temp.shape[0]==0:
        return err
    else:

        earn_column = fun.get_earnings_column(inflation, salary, benefits)
        if earn_column=="":
            return err

        if df_temp.shape[0]==0 :
            return err

        df_temp = df_temp[df_temp[earn_column]>=salaries[0]]
        if (salaries[1]<600000):
            df_temp = df_temp[df_temp[earn_column]<=salaries[1]]

        if df_temp.shape[0]==0:
            return err
        df_temp = df_temp[['_gender_x','first_name',earn_column, 'employer']]
        df_temp.columns=['_gender_x','first_name','salary_x', 'employer']

        temp = []

        temp.append([df_temp.shape[0], df_temp[df_temp._gender_x=='female'].shape[0], df_temp[df_temp._gender_x=='male'].shape[0],
            (df_temp[df_temp._gender_x=='female'].shape[0] / (df_temp[df_temp._gender_x=='female'].shape[0]+df_temp[df_temp._gender_x=='male'].shape[0])*100),
            df_temp.salary_x.mean(),df_temp[df_temp._gender_x=='male'].salary_x.mean(),df_temp[df_temp._gender_x=='female'].salary_x.mean(),
            (df_temp[df_temp._gender_x=='female'].salary_x.mean() - df_temp[df_temp._gender_x=='male'].salary_x.mean())
            ])

        df_temp1 = pd.DataFrame(temp)
        df_temp1.columns = ['Total Employees','Total (women)','Total (men)', 'Percent (women)','Average salary','Average salary (woman)',
        'Average salary (man)', 'Difference']

        div1 = html.Div(children = fun.generate_table(df_temp1, title = "Totals" , display_columns=True,
            dtypes = ["num","num","num","per", "dol","dol", "dol", "dol"], col_to_highlight_negatives=[7], col_to_highlight_negatives_per=[3]))

        # add largest employeers in the sector
        df_temp2 = pd.DataFrame(df_temp.groupby(['employer']).agg({'first_name':np.size, 'salary_x':np.mean}))
        df_temp2 = df_temp2.reset_index().sort_values('first_name', ascending=False)[:5]
        df_temp2.columns = [' ', "Total Employees on Sunshine List","Average Salary"]

        # div2 = html.Div(children = fun.generate_table(df_temp2,title='Largest Employers in this Sector', 
        #     display_columns=True,dtypes=["","num"])),
        div2 = html.Div(children = fun.generate_table(df_temp2, title = "Largest Employers in this Sector" , display_columns=True,
        dtypes = ["","num","dol"]))
        return [div1, div2]