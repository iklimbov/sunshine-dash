import dash
import pandas as pd

import os
import flask

# init the app
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

# add custom css
css_directory = os.getcwd()
stylesheets = ['sunshine.css']
static_css_route = '/static/assests/'

@app.server.route('{}<stylesheet>'.format(static_css_route))
def serve_stylesheet(stylesheet):
    return flask.send_from_directory(css_directory+"/assests/", stylesheet)

for stylesheet in stylesheets:
    app.css.append_css({"external_url": static_css_route+"{}".format(stylesheet)})

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# external_stylesheets = ['https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/css/bootstrap.min.css']
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# read data
df = pd.read_csv('data/2008_2018_first_tab.csv.bz2', compression='bz2', header=0, sep=',', quotechar='"')
df18 = pd.read_csv('data/2018prod.csv.bz2', compression='bz2', header=0, sep=',', quotechar='"')

# global variables
YEARS = [i for i in range(2008,2019)]

SECTORS = list(df18._sector.unique())
SECTORS.sort()


POSITIONS = ['other', 'analyst', 'associate dean', 'ceo', 'cfo',  'chro', 'chief','cto', 
'director', 'doctor', 'executive director', 'firefighter', 'manager', 'minister', 'nurse', 
'paramedic', 'police person', 'professor', 'superintendent', 'supervisor', 'teacher', 'vp']

POSITION_LABLES = ['Other','Analyst', 'Associate Dean', 'CEO','CFO','CHRO','C-Suite',
'CTO', 'Director','Doctor', 'Executive Director', 'Firefighter', 'Manager', 'Minister', 
'Nurse', 'Paramedic', 'Police Person', 'Professor', 'Superintendent', 'Supervisor', 'Teacher', 'VP' ]

EARNINGS = [0,100000,200000,300000,400000,500000,600000 ]
EARNING_LABLES = ['0','100K','200K','300K','400K','500K','more...' ]

CURRENT_YEAR = 2018

COLORS = {
    'background': '#333333',
    'text': '#7FDBFF',
    'cmale':'#4363d8',
    'cfemale': '#f58231'
}

SORT_RATINGS_LABLES =['Average Rating', 'Culture',
        'Work, Life Balance', 'Salary, benefits', "Job Security, Advancement", 'Mgmt', 'CEO approval']

SORT_RATINGS= ['avg_indeed_score','culture', 'work_life', 'salary','job_security', 'management', 'ceo']