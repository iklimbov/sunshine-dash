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
                            options=[{'label': i ,'value':i} for i in ['Benefits']],
                            values=[],
                            
                )],className=['col-sm-4'] ),
                html.Div([dcc.Checklist(
                            id='include_salary2',
                            options=[{'label': i ,'value':i} for i in ['Salary']],
                            values=['Salary'],
                            
                )],className=['col-sm-4'] ),
        ],className='col-sm-6'),
        html.Div([
            html.Div([
                  html.Div([
                      html.H5(children='Sector (leave blank for all):'),
                      dcc.Dropdown(
                                  id='sector_select2',
                                  clearable=True,
                                  options=[{'label': i, 'value': i} for i in db_app.SECTORS],
                                  # value = 'Universities'
                  )]),
                  html.Div([
                      html.H5(children='Employer I :'),                      
                      dcc.Dropdown(
                                  id='companies_select2a',
                                  clearable=True,
                                  # value = 'Trent University'
                  )]),
                  html.Div([
                      html.H5(children='Employer II:'),
                      dcc.Dropdown(
                                  id='companies_select2b',
                                  clearable=True,
                                  # value= 'Ryerson University'
                  )]),

            ],className=['container-fluid']),
        ],className='col-sm-3'),
        html.Div([
          html.Div([

                  html.Div([
                    html.H5(
                        children='Role (leave blank for all):'),
                    dcc.Dropdown(
                        id='position_select2',
                        options=[{'label': ii, 'value': i} for i, ii in zip(db_app.POSITIONS, db_app.POSITION_LABLES)],
                        value='',
                        clearable=True,
                   )]),
             ],className='container-fluid'),
        ],className='col-sm-3'),

    ],className='container-fluid well'),  
    html.H3(id = 'dist_title'),  
    html.Div([
        html.Div ([
            dcc.Graph(id='dist_graph1'),
        ],className=['col-sm-4']),
        html.Div ([
            dcc.Graph(id='dist_graph2'),
        ],className=['col-sm-4']),
        html.Div ([
            dcc.Graph(id='dist_graph3'),
        ],className=['col-sm-4']),
    ],className='col-sm-12 container-fluid'),
    html.H3(id='summary_title'),  
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

###############################################################################
# Distribution graph - for the selected sector
# takes into account earnings columns and position
###############################################################################
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
        return fun.get_default_graph()

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

###############################################################################
# Distribution graph - for the selected sector and company I
# takes into account earnings columns and position
###############################################################################
@app.callback(
    Output(component_id='dist_graph2', component_property='figure'),
    [Input(component_id='sector_select2', component_property='value'),
    Input(component_id='companies_select2a', component_property='value'),
    Input(component_id='position_select2', component_property='value'),
    Input(component_id='inflation_ajust2', component_property='values'),
    Input(component_id='include_benefits2', component_property='values'),
    Input(component_id='include_salary2', component_property='values'),
    Input(component_id='salary_slider2', component_property='value')])
def cbg3(sector, company, position, inflation, benefits, salary, salaries):
    if (company==None or sector==None or company=='None'):
        return fun.get_default_graph()

    df_temp = db_app.df18.copy()

    if position!='' and position!=None:
        if position=='chief':
            df_temp=df_temp[df_temp.job_category2=='chief']
        else :
            df_temp=df_temp[df_temp.job_category1==position]

    if (sector != None):
        df_temp = df_temp[df_temp._sector == sector]

    df_temp = df_temp[df_temp.employer==company]

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

    return  fun.format_dist_graph_data(df_f, df_m, company)


###############################################################################
# Distribution graph - for the selected sector and company II
# takes into account earnings columns and position
###############################################################################
@app.callback(
    Output(component_id='dist_graph3', component_property='figure'),
    [Input(component_id='sector_select2', component_property='value'),
    Input(component_id='companies_select2b', component_property='value'),
    Input(component_id='position_select2', component_property='value'),
    Input(component_id='inflation_ajust2', component_property='values'),
    Input(component_id='include_benefits2', component_property='values'),
    Input(component_id='include_salary2', component_property='values'),
    Input(component_id='salary_slider2', component_property='value')])
def cbg3(sector, company, position, inflation, benefits, salary, salaries):
    if (company==None or sector==None or company=='None'):
        return fun.get_default_graph()

    df_temp = db_app.df18.copy()

    if position!='' and position!=None:
        if position=='chief':
            df_temp=df_temp[df_temp.job_category2=='chief']
        else :
            df_temp=df_temp[df_temp.job_category1==position]

    if (sector != None):
        df_temp = df_temp[df_temp._sector == sector]

    df_temp = df_temp[df_temp.employer==company]

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

    return  fun.format_dist_graph_data(df_f, df_m, company)

###############################################################################
# SUMMARY BOX - for selected sector
# takes into account earnings columns and position
###############################################################################
@app.callback(
    Output(component_id='dist_summary1', component_property='children'),
    [Input(component_id='sector_select2', component_property='value'),
    Input(component_id='position_select2', component_property='value'),
    Input(component_id='inflation_ajust2', component_property='values'),
    Input(component_id='include_benefits2', component_property='values'),
    Input(component_id='include_salary2', component_property='values'),
    Input(component_id='salary_slider2', component_property='value')])
def sb2_adjust(sector, position, inflation, benefits, salary, salaries):

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

    return fun.generate_table(df_temp, title = str(sector) , display_columns=True, 
        dtypes = ["","num","num","per","dol","dol","dol"], col_to_highlight_negatives=6)


###############################################################################
# Returns first subtitle or an information box
###############################################################################
@app.callback(
    Output(component_id='dist_title', component_property='children'),
    [Input(component_id='sector_select2', component_property='value'),
    Input(component_id='companies_select2a', component_property='value'),
    Input(component_id='companies_select2b', component_property='value'),])
def cbg2(sector, company1, company2):
    
    if sector == None:
        return html.Div(children = 'Select Sector and upto two Companies to Compare',className= ['alert alert-info'])
    txt = sector
    if company1 is None and (not company2 is None):
        company1= company2
        company2 = None
    try:
        txt += ": " + company1
    except:
        pass
    finally:
        try:
            txt += " vs " + company2
        except:
            pass
    return txt

###############################################################################
# Returns second subtitle 
###############################################################################
@app.callback(
    Output(component_id='summary_title', component_property='children'),
    [Input(component_id='sector_select2', component_property='value'),
    Input(component_id='companies_select2a', component_property='value'),
    Input(component_id='companies_select2b', component_property='value'),])
def cbg2(sector, company1, company2):
    
    if sector == None:
        return ""
    txt = "Quartile Summary for " + sector
    if company1 is None and (not company2 is None):
        company1= company2
        company2 = None
    try:
        txt += ". " + company1
    except:
        pass
    finally:
        try:
            txt += " vs " + company2
        except:
            pass
    return txt


###############################################################################
# SUMMARY BOX - for selected company I
# takes into account earnings columns and position
###############################################################################
@app.callback(
    Output(component_id='dist_summary2', component_property='children'),
    [Input(component_id='sector_select2', component_property='value'),
    Input(component_id='companies_select2a', component_property='value'),
    Input(component_id='position_select2', component_property='value'),
    Input(component_id='inflation_ajust2', component_property='values'),
    Input(component_id='include_benefits2', component_property='values'),
    Input(component_id='include_salary2', component_property='values'),
    Input(component_id='salary_slider2', component_property='value'),])
def sb3_adjust( sector, company, position, inflation, benefits, salary, salaries):
    if (company==None or sector==None or company=='None'):
        return ""

    df_temp = db_app.df18.copy()

    if position!='' and position!=None:
        if position=='chief':
            df_temp=df_temp[df_temp.job_category2=='chief']
        else :
            df_temp=df_temp[df_temp.job_category1==position]

    df_temp = df_temp[df_temp.employer==company]

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

    return fun.generate_table(df_temp, title = str(company) , display_columns=True, 
        dtypes = ["","num","num","per","dol","dol","dol"], col_to_highlight_negatives=6)

###############################################################################
# SUMMARY BOX - for selected company II
# takes into account earnings columns and position
###############################################################################
@app.callback(
    Output(component_id='dist_summary3', component_property='children'),
    [Input(component_id='sector_select2', component_property='value'),
    Input(component_id='companies_select2b', component_property='value'),
    Input(component_id='position_select2', component_property='value'),
    Input(component_id='inflation_ajust2', component_property='values'),
    Input(component_id='include_benefits2', component_property='values'),
    Input(component_id='include_salary2', component_property='values'),
    Input(component_id='salary_slider2', component_property='value'),])
def sb3_adjust( sector, company, position, inflation, benefits, salary, salaries):
    if (company==None or sector==None):
        return ""
    df_temp = db_app.df18.copy()

    if position!='' and position!=None:
        if position=='chief':
            df_temp=df_temp[df_temp.job_category2=='chief']
        else :
            df_temp=df_temp[df_temp.job_category1==position]
  

    df_temp = df_temp[df_temp.employer==company]

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

    return fun.generate_table(df_temp, title = str(company) , display_columns=True, 
        dtypes = ["","num","num","per","dol","dol","dol"], col_to_highlight_negatives=6)



###############################################################################
# POPULATE COMPANIES I BASED ON SECTOR SELECTED
###############################################################################
@app.callback(
    Output(component_id='companies_select2a', component_property= 'options'),
    [Input(component_id='sector_select2', component_property='value')])
def call1(value):
    return fun.get_companies_for_sector(value,db_app.df18)
@app.callback(
    Output(component_id='companies_select2a', component_property='value'),
    [Input(component_id='sector_select2', component_property='value')])
def call22(value):
    if (value==None ):
        return None

###############################################################################
# POPULATE COMPANIES II BASED ON SECTOR SELECTED
###############################################################################
@app.callback(
    Output(component_id='companies_select2b', component_property= 'options'),
    [Input(component_id='sector_select2', component_property='value')])
def call1(value):
    return fun.get_companies_for_sector(value,db_app.df18)

@app.callback(
    Output(component_id='companies_select2b', component_property='value'),
    [Input(component_id='sector_select2', component_property='value')])
def call22(value):
    if (value==None ):
        return None


###############################################################################
# List of roles for this sector 
###############################################################################
@app.callback(
    Output(component_id='position_select2', component_property= 'options'),
    [Input(component_id='sector_select2', component_property='value')])
def call1(value):
    return fun.get_roles(value, db_app.df18)

@app.callback(
    Output(component_id='position_select2', component_property= 'value'),
    [Input(component_id='sector_select2', component_property='value'),
    Input(component_id='companies_select2a', component_property='value')])
def call11(value, value1):
    return None


       