import dash_html_components as html
import pandas as pd
import numpy as np

import db_app
from db_app import app


###############################################################################
# FUNCTIONS
# 
###############################################################################

##############################################################################
# creates html table out of DataFrame
# one row can be highlighted,
# if data types are passed, values are formatted 
##############################################################################
def generate_table(dataframe, max_rows=20, title = "", display_columns = True, dtypes = [], highlight_row = -1, col_to_highlight_negatives=-1):

    def format_me(use_dtypes, s,f):
        if s!=s:
            return ""
        if use_dtypes == False:
            return s
        if f == "":
            return s
        if f == 'num':
            return "{:,}".format(int(s))
        if f == 'per':
            return str(s)+"%"
        if f == 'dol':
            return "$" + "{:,}".format(int(s))
        else:
            return "Format ERROR: "+f

    def get_red(val,ctr):
        if ctr != col_to_highlight_negatives:
            return "none"
        try:
            x = float(val)
            if x < 0:
                return "red_field"
            else:
                return "green_field"
        except:
            return "none"

    if (len(title)>0):
        title = html.H4(children = title)

    use_dtypes = False
    if (len(dtypes) == len(dataframe.columns)):
        use_dtypes = True
    else:
        dtypes = [""] * len(dataframe.columns)

    cols = []
    if (display_columns):
        cols = [html.Tr([html.Th(col) for col in dataframe.columns])]

    highlight = 'highlight_row'
    classes = ["none" if int(i) != int(highlight_row) else highlight for i in range(0, len(dataframe))]

    red = 'red_field'
    classes_td = [([get_red(dataframe.iloc[i][col],cyr) for col,cyr in zip(dataframe.columns, range(0,len(dataframe.columns)))]) for i in range(min(len(dataframe), max_rows))]

    body = (
        cols +
        # Body
        [html.Tr([
            html.Td(format_me(use_dtypes,dataframe.iloc[i][col],ii),className = row_class) for col, ii, row_class in zip(dataframe.columns,dtypes, row_classes)
        ],
            className = iii
        ) for i, iii, row_classes in zip (range(min(len(dataframe), max_rows)),classes, classes_td )])

    table =  html.Table(
        body
    )

    return [title, table]

##############################################################################
# based on passed parameters, returns the name of the column 
# to be used as 'earnings'
# possible values:
# - salary
# - benefits
# - salary + benefits
# values can also be adjusted for inflation 
##############################################################################
def get_earnings_column(inflation, salary, benefits):
        salary = len (salary)
        benefits = len( benefits)
        inflation = len (inflation)

        if (salary==0 and benefits==0):
            return ""

        if (salary==0 and benefits>0):
            # only benefits
            if inflation >0:
                return 'benifits_adjusted'
            else:
                return 'benefits'

        if (salary>0 and benefits==0):
            # only benefits
            if inflation >0:
                return 'salary_adjusted'
            else:
                return 'salary_x'

        if (salary>0 and benefits>0):
            # only benefits
            if inflation >0:
                return 'salary_adjusted_total'
            else:
                return 'salary_total'


##############################################################################
# Returns empty graph (black space with nothing on it)
##############################################################################
def get_default_graph(height = 0, title = '', bg_color = 'white'):


    rn = {
            'data': [
            ],
            'layout': {
                'title': title,
                'plot_bgcolor': bg_color,
                'paper_bgcolor': bg_color,
                'font': {
                    'color': db_app.COLORS['text'],
                    'size':'120%'},
                'margin':{'t':'1em','r':40,'l':(37*7),'b':50},
                'showlegend':False,
                'yaxis':dict(showticklabels=False, showgrid=False, zeroline=False, showline=False),
                'xaxis':dict(showticklabels=False, showgrid=False, zeroline=False, showline=False),
            }
        }

    if height>0:
        rn['layout']['height']=height

    return rn 

##############################################################################
# Distribution graph 
##############################################################################
def create_dist_graph(sector, company, position, inflation, benefits, salary, salaries):
    if (sector==None):
        return get_default_graph()

    df_temp = db_app.df18[db_app.df18._sector==sector].copy()

    if (company != None):
        df_temp = df_temp[df_temp.employer==company]

    if df_temp.shape[0]==0:
        return get_default_graph()

    if position!='' and position!=None:
        if position=='chief':
            df_temp=df_temp[df_temp.job_category2=='chief']
        else :
            df_temp=df_temp[df_temp.job_category1==position]

    if df_temp.shape[0]==0:
        return get_default_graph()
    else:

        earn_column = get_earnings_column(inflation, salary, benefits)
        if earn_column=="":
            return get_default_graph()

        if df_temp.shape[0]==0 :
            return get_default_graph()

        df_temp = df_temp[df_temp[earn_column]>=salaries[0]]
        if (salaries[1]<600000):
            df_temp = df_temp[df_temp[earn_column]<=salaries[1]]

        if df_temp.shape[0]==0:
            return get_default_graph()

        df_temp = df_temp[['_gender_x','first_name',earn_column]]
        df_temp.columns=['_gender_x','first_name','salary_x']

        df_m= df_temp[df_temp._gender_x.astype(str)=='male']
        df_f= df_temp[df_temp._gender_x.astype(str)=='female']

    return  format_dist_graph_data(df_f, df_m, sector)

##############################################################################
# Distribution graph data format
##############################################################################
def format_dist_graph_data(df_f,df_m, title ):

    gr_layout = {
            'plot_bgcolor': db_app.COLORS['background'],
            'paper_bgcolor': db_app.COLORS['background'],
            'font': {
                'color': db_app.COLORS['text'],
                'size': '120%'},
            'visible':'legendonly',
            # 'title': title,
            'margin':{'t':5,'r':1,'l':50,'b':40},
            'height': 500,
            'legend':{'orientation':"h"},
            'yaxis':dict(title = '',gridcolor='white', gridwidth=0.3, hoverformat = ',2f', tickformat = ',2f'),
            'xaxis':dict(title = '',hoverformat = '$,2f', tickformat = '$,2f'),
    }
    data =  [
            {
                'x': df_m.salary_x.astype(int),
                'name': 'Men',
                'type': 'histogram',
                'nbinsx': 20,
                # 'opacity':0.6,
                'margin': '0.5em',
                'marker':{'color':db_app.COLORS['cmale']}
            },
            {
                'x': df_f.salary_x.astype(int),
                'name': 'Women',
                'type': 'histogram',
                'nbinsx': 20,
                # 'opacity':0.6,
                'margin': '0.5em',
                'marker':{'color':db_app.COLORS['cfemale']}
            },
        ]
    temp = {
        'data': data, 
        'layout': gr_layout
    }
    return temp

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
        earn_column = get_earnings_column(inflation, salary, benefits)
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

        df_temp['per_female'] = get_f_count_number(df_temp.first_name_x, df_temp.first_name_y)
        df_temp['difference'] = df_temp.apply(lambda x: x.salary_x_x - x.salary_x_y, axis = 1)

        df_temp = df_temp[['range','first_name_x','first_name_y','per_female','salary_x_x','salary_x_y', 'difference']]
       

        additional.columns=df_temp.columns
        additional['per_female'] = get_f_count_number(additional.first_name_x, additional.first_name_y)
        additional['difference'] = additional.apply(lambda x: x.salary_x_x - x.salary_x_y, axis = 1)

        df_temp = pd.concat([df_temp,additional], axis=0)


        df_temp.columns = ['Quartile','Total (women)','Total (men)', 'Percent (women)','Average salary (woman)','Average salary (man)', 'Difference']

    return generate_table(df_temp, title = "" , display_columns=True, 
        dtypes = ["","num","num","per","dol","dol","dol"], col_to_highlight_negatives=6)


##############################################################################
# Horizontal stack graph
##############################################################################
def format_h_stack_graph_data(df_f,df_m, ycolumn,xcolumn, title, height=400):
    return {
            'data': [
                {'y': df_m[ycolumn], 'x': df_m[xcolumn], 'type': 'bar', 'name': 'Men','textfont':{'size':20}, 'orientation':'h',
                'marker':{'color':db_app.COLORS['cfemale']}},
                {'y': df_f[ycolumn], 'x': df_f[xcolumn], 'type': 'bar', 'name': 'Women','textfont':{'size':20}, 'orientation':'h',
                'marker':{'color':db_app.COLORS['cmale']}},
            ],
            'layout': {
                'barmode':'stack',
                'title': title,
                'plot_bgcolor': db_app.COLORS['background'],
                'paper_bgcolor': db_app.COLORS['background'],
                'font': {
                    'color': db_app.COLORS['text'],
                    'size':'120%'},
                'margin':{'t':'1em','r':40,'l':(37*7),'b':50},
                'height': height,
                'legend':{'orientation':"h"},
                'xaxis':dict(showticklabels=False,gridcolor='white', gridwidth=0.5)
            }
        }

##############################################################################
# returns % of the first value 
##############################################################################
def get_f_count_number(f, m):

    ret = []
    for a, b in zip (f,m):
        a = float(a)
        b = float(b)
        try:
            ret.append(int(a/(a+b)*100))
        except:
            ret.append(0)
    return ret

##############################################################################
# returns % of the second value 
##############################################################################
def get_m_count_number(f, m):

    ret = []
    for a, b in zip (f,m):
        a = float(a)
        b = float(b)
        try:
            ret.append(int(b/(a+b)*100))
        except:
            ret.append(0)
    return ret


##############################################################################
# returns % of the first value with '%' sign
##############################################################################
def get_f_count(f, m):

    ret = []
    for a, b in zip (f,m):
        a = float(a)
        b = float(b)
        try:
            ret.append( str(int(a/(a+b)*100)) + "%")
        except:
            ret.append(0)
    return ret

##############################################################################
# returns % of the second value with '%' sign
##############################################################################
def get_m_count(f, m):

    ret = []
    for a, b in zip (f,m):
        a = float(a)
        b = float(b)
        try:
            ret.append(str(int(b/(a+b)*100)) + "%")
        except:
            ret.append(0)
    return ret


##############################################################################
# Returns min of two lists + 5%
# That is used to display bottom of bar graphs, so the smallest bar is visible
##############################################################################
def get_min_plus_5(f,m):
    plus = 0
    mm = 0
    try:
        mm = min(list([f.min(),m.min()]))
        plus = round(mm*0.1)
    except Exception as ex:
        # app.logger.warning(ex)
        pass
    finally:
        return mm-plus

##############################################################################
# Returns a list of Roles for the given sector 
##############################################################################
def get_roles(sector,df):
    temp = df
    if sector!= 'None' and sector!= None:
        temp = temp[temp._sector==sector]

    ret1 = temp.job_category1.unique()
    ret1 = list(ret1)
    ret1.sort()
    options = []
    options.append({'label': 'Other' , 'value': 'other'})
    options.append({'label': 'C-Suite' , 'value': 'chief'})
    for i in ret1:
        if i != 'other':
            options.append({'label': i.capitalize() , 'value': i})

    return options

##############################################################################
# Returns list of companies for the given sector
##############################################################################
def get_companies_for_sector(sector, df):
    temp = df[df._sector==sector]
    options=[]
    ret1 = temp.employer.unique()
    ret1 = list(ret1)
    ret1.sort()
    for i in ret1:
        options.append({'label': i, 'value': i})
    return options

##############################################################################
# Checks to see if the value is in the options of the check box 
# array of dictionaries
##############################################################################
def in_options(options,value):

    if options is None:
        return False

    for i in options:
        k = i['label']
        if k == value:
            return True

    return False
