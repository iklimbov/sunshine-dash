import dash
import pandas as pd

app = dash.Dash(__name__)

app.config.suppress_callback_exceptions = True

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# external_stylesheets = ['https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/css/bootstrap.min.css']
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)



# df =  pd.read_csv('data/2008_2018prod.csv')
# df =  pd.read_csv('data/2008prod.csv')
# df = pd.read_csv('https://s3.ca-central-1.amazonaws.com/sunshinelist/2008_2018prod.csv.bz2', compression='bz2', header=0, sep=',', quotechar='"')

# df = pd.read_csv('data/2008_2018prod.csv.bz2', compression='bz2', header=0, sep=',', quotechar='"')

df = pd.read_csv('data/2008_2018_first_tab.csv.bz2', compression='bz2', header=0, sep=',', quotechar='"')
df18 = pd.read_csv('data/2018prod.csv.bz2', compression='bz2', header=0, sep=',', quotechar='"')

YEARS = [i for i in range(2008,2019)]

SECTORS = ['Colleges',
'Crown Agencies',
'Government of Ontario - Judiciary',
'Government of Ontario - Ministries',
'Hospitals and Boards of Public Health',
'Hydro One and Ontario Power Generation',
'Legislative Assembly and Offices',
'Municipalities and Services',
'Other Public Sector Employers',
'Primary/Secondary Education',
'Universities']

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