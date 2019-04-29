import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import logging
import gunicorn

import os
import flask

import db_app
from db_app import app
from apps import tabs

# app and server made available here for Flask to run
app = db_app.app
server = db_app.server

# app.logger.debug("this is a DEBUG message")
# app.logger.info("this is an INFO message")
# app.logger.warning("this is a WARNING message")
# app.logger.error("this is an ERROR message")
# app.logger.critical("this is a CRITICAL message")

# main page layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


app.logger.error(db_app.base_dir)

@app.server.route("/about")
def get_info_page():
    return flask.send_from_directory(db_app.base_dir+"/assests/", "about.html")

# we only have one page at the moment, with multile tabs
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
      return tabs.layout
    if pathname == '/about':
      return get_info_page()
    else:
      return '404'

if __name__ == '__main__':
    app.run_server(debug=True)
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)