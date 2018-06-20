# -*- encoding: utf-8 -*-
"""
Python Aplication Template
Licence: GPLv3
"""

from flask import url_for, redirect, render_template, flash, g, session
# from flask_login import login_user, logout_user, current_user, login_required
from app import app
from forms import ExampleForm, LoginForm
from app.models import *
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo

import requests

#----------------CORS IMPLEMENTATION-------------
from datetime import timedelta  
from flask import Flask, make_response, request, current_app  
from functools import update_wrapper


def crossdomain(origin=None, methods=None, headers=None, max_age=21600, attach_to_all=True, automatic_options=True):  
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


@app.route('/things', methods=['GET'])
@crossdomain(origin='*')
def get_all_terrain():
  terrain = Terrain
  sensor = Sensor
  variables = Variable
  alertas = Alert

  output = []
  s_var = 0
  
  for i in sensor.objects:
    if sensor.objects[0].state == True:
      s_var = s_var + 1

  output.append({'terrain' : terrain.objects.count(), 'sensor' : s_var,
   'variables' : variables.objects.count(), 'alertas': alertas.objects.count()})
  print output
  return jsonify({'result' : output})

@app.route('/terrain_create', methods=['POST'])
@crossdomain(origin='*')
def add_terrain():
  terrain = Terrain
  name = request.json['name']
  height = request.json['height']
  width = request.json['width']
  t_id = terrain.objects.create(name=name,height=height,width=width)
  output = {'CREATED' : t_id['name'], 'height' : t_id['height'], 'width' : t_id['width']}
  return jsonify({'result' : output})



@app.route('/')
@crossdomain(origin='*')
def index():
  return render_template('index.html')

@app.route('/dashboard')
@crossdomain(origin='*')
def viewDashboard():
  t = requests.get('http://localhost:4000/terrain').content
  print t
  return "Prueba dashboard"

