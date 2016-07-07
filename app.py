"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

This file creates your application.
"""

import os
from flask import Flask, Response, render_template, request, redirect, url_for
import flask
app = Flask(__name__)
from flask_cors import *
import requests
from requests.auth import HTTPBasicAuth
import re
import json
import urllib
import psycopg2
from datetime import datetime
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'this_should_be_configured')
psql_host = os.environ.get('psql_host')
psql_port = os.environ.get('psql_port')
psql_username = os.environ.get('psql_username')
psql_password = os.environ.get('psql_password')
psql_dbname = os.environ.get('psql_dbname')
import sys
import logging

#@app.before_request
def log_request():
    pass
        
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')

import requests
import re

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")

@app.route('/query/')
@cross_origin()
def for_socrata_owned_datasets():
    query = request.args.get('q')
    d = {'query': query}
    conn_string = "dbname='%s' user='%s' host='%s' password='%s' port='%s'" % (psql_dbname, psql_username, psql_host, psql_password, psql_port)
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    cur.execute(query)
    
    d['rows'] = [dict((cur.description[i][0], value) \
           for i, value in enumerate(row)) for row in cur.fetchall()]
    d['number_of_rows'] = len(d['rows'])
    d['fields'] = d['rows'][0].keys() if d['rows'] else []
    conn.close()
    return Response(json.dumps(d, default=json_serial), mimetype='application/json')

@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', debug=True, port=port)
