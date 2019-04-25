import dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc

from db_app import app
import db_app
from apps import db_app1, db_app2, db_app2a, db_app3, db_app4

layout = html.Div([
    html.H1('Sunshine List Ontario'),
    dcc.Tabs(id="tabs-sunshine", value='tab-1', children=[
        dcc.Tab(label='Ten-Year Outlook', value='tab-1', className='custom-tab nav nav-tabs nav-justified report_tab',
                selected_className='custom-tab-active nav nav-pills active'),
        # dcc.Tab(label='2018 Employer Comparison', value='tab-2', className='nav nav-tabs nav-justified custom-tab',
        #         selected_className='nav nav-pills active custom-tab-active'),
        dcc.Tab(label='2018 Employer Comparison', value='tab-3', className='nav nav-tabs nav-justified custom-tab',
                selected_className='nav nav-pills active custom-tab-active'),
        dcc.Tab(label='2018 Employer Ranking', value='tab-4', className='nav nav-tabs nav-justified custom-tab',
                selected_className='nav nav-pills active custom-tab-active'),
    ]),
    html.Div([
        dcc.Store(id='storage')
    ],
            id="hiddendata",
            style={"display": "none"},
    ),
    html.Div(id='tabs-content')
])


@app.callback(Output('tabs-content', 'children'),
              [Input('tabs-sunshine', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return db_app1.layout
    # elif tab == 'tab-2':
    #     return db_app2.layout
    elif tab == 'tab-3':
        return db_app2a.layout
    elif tab == 'tab-4':
        return db_app4.layout

