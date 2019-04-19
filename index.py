import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask import send_from_directory

import os
import flask

import db_app
from db_app import app
from apps import db_app1, db_app2, tabs


app = db_app.app
server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/db_app1':
         return db_app1.layout
    elif pathname == '/apps/db_app2':
         return tabs.layout
    else:
        return '404'

css_directory = os.getcwd()
stylesheets = ['sunshine.css']
static_css_route = '/static/assests/'


@app.server.route('{}<stylesheet>'.format(static_css_route))
def serve_stylesheet(stylesheet):
    return flask.send_from_directory(css_directory+"/assests/", stylesheet)


for stylesheet in stylesheets:
    app.css.append_css({"external_url": static_css_route+"{}".format(stylesheet)})

if __name__ == '__main__':
    app.run_server(debug=True)