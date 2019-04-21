import dash_html_components as html

import db_app


###############################################################################
# FUNCTIONS
# 
###############################################################################

##############################################################################
# creates html table out of DataFrame
# one row can be highlighted,
# if data types are passed, values are formatted 
##############################################################################
def generate_table(dataframe, max_rows=20, title = "", display_columns = True, dtypes = [], highlight_row = -1):

    def format_me(use_dtypes, s,f):
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

    body = (
        cols +
        # Body
        [html.Tr([
            html.Td(format_me(use_dtypes,dataframe.iloc[i][col],ii)) for col, ii in zip(dataframe.columns,dtypes)
        ],
            className = iii
        ) for i, iii in zip (range(min(len(dataframe), max_rows)),classes )])

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
# Distribution graph
##############################################################################
def format_dist_graph_data(df_f,df_m, title ):

    gr_layout = {
            'plot_bgcolor': db_app.COLORS['background'],
            'paper_bgcolor': db_app.COLORS['background'],
            'font': {
                'color': db_app.COLORS['text'],
                'size': '120%'},
            'visible':'legendonly',
            'title': title,
            'margin':{'t':'1em','r':1,'l':50,'b':50},
            'height': 700,
            'legend':{'orientation':"h"},
            'yaxis':dict(title = 'Employee Count per Salary Category',gridcolor='white', gridwidth=0.3),
    }
    data =  [
            {
                'x': df_m.salary_x.astype(int),
                'name': 'Male',
                'type': 'histogram',
                'nbinsx': 20,
                # 'opacity':0.6,
                'margin': '1em',
                'marker':{'color':db_app.COLORS['cmale']}
            },
            {
                'x': df_f.salary_x.astype(int),
                'name': 'Female',
                'type': 'histogram',
                'nbinsx': 20,
                # 'opacity':0.6,
                'margin': '1em',
                'marker':{'color':db_app.COLORS['cfemale']}
            },
        ]
    temp = {
        'data': data, 
        'layout': gr_layout
    }
    return temp

##############################################################################
# Horizontal stack graph
##############################################################################
def format_h_stack_graph_data(df_f,df_m, ycolumn,xcolumn, title, height=400):
    return {
            'data': [
                {'y': df_m[ycolumn], 'x': df_m[xcolumn], 'type': 'bar', 'name': 'Male','textfont':{'size':20}, 'orientation':'h',
                'marker':{'color':db_app.COLORS['cfemale']}},
                {'y': df_f[ycolumn], 'x': df_f[xcolumn], 'type': 'bar', 'name': 'Female','textfont':{'size':20}, 'orientation':'h',
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