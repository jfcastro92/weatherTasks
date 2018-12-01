# -*- encoding: utf-8 -*-
"""
Poryecto de grado: WeatherTasks Version 1.0
Juan Fernando Castro Mesa - Ingenieria Sistemas y Computacion
Pontificia Universidad Javeriana Cali - 2018

"""

import json
import datetime
import requests

from flask import url_for, redirect, render_template, flash, g, session
from app import app
#from forms import ExampleForm, LoginForm
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
from mongoengine.queryset.visitor import Q
from app.models import *




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


@app.route('/things/', methods=['GET'])
@crossdomain(origin='*')
def get_all_terrains():
  output = []
  s_var = Sensor.objects(state=True).count()


  output.append({'terrain' : Terrain.objects.count(), 'sensor' : s_var,
   'variables' : Variable.objects.count(),
    'alertas': Alert.objects(value_timestamp__gt = str(datetime.datetime.now()-datetime.timedelta(days=1))).count()})
  return jsonify({'result' : output})

@app.route('/terrainsget/', methods=['GET'])
@crossdomain(origin='*')
def get_all_terrain():
  data = []

  for terrain in Terrain.objects:
    output = {}
    s_data = {}
    a_data = {}

    output['id'] = str(terrain.id)
    output['name'] = terrain.name
    output['description'] = terrain.description
    output['height'] = terrain.height
    output['width'] = terrain.width
    output['lat'] = terrain.lat
    output['lon'] = terrain.lon
    sensors = []
    alerts = []
    for sensor in Sensor.objects(terrain_object = terrain):
      s_data = {"id": str(sensor.id),"name": sensor.name, "state": sensor.state, "description": sensor.description}
      sensors.append(s_data)
    for alert in Alert.objects(terrain_object = terrain, value_timestamp__gt = str(datetime.datetime.now()-datetime.timedelta(days=1))):
      a_data = {"id": str(alert.id), "description": alert.description}
      alerts.append(a_data)

    output['sensor'] = sensors  
    output['alert'] = alerts
    data.append(output)

  return jsonify({'result' : data})


@app.route('/alertsget/', methods=['GET'])
@crossdomain(origin='*')
def get_all_alerts():

  data = []
  for alert in Alert.objects(value_timestamp__gt = str(datetime.datetime.now()-datetime.timedelta(days=1))):
    output = {}
    s_data = {}
    t_data = {}
    v_data = {}

    output['id'] = str(alert.id)
    output['data'] = alert.data
    output['description'] = alert.description
    output['alert_type'] = alert.alert_type
    output['value_timestamp'] = str(alert.value_timestamp)

    sensor = {"id": str(alert.sensor_object.id), "name": alert.sensor_object.name, 
              "state": alert.sensor_object.state, "description": alert.sensor_object.description}
    
    terrain = {"id": str(alert.terrain_object.id),"name": alert.terrain_object.name, 
              "lat": alert.terrain_object.lat, "lon": alert.terrain_object.lon, 
              "description": alert.terrain_object.description}

    variable = {"id": str(alert.variable_object.id),"name": alert.variable_object.name,
             "unit": alert.variable_object.unit, "alert_max": alert.variable_object.alert_max,
             "alert_min": alert.variable_object.alert_min, "max_value": alert.variable_object.max_value, 
             "min_value": alert.variable_object.min_value}

    output['sensor'] = sensor
    output['terrain'] = terrain
    output['variable'] = variable
    data.append(output)

  return jsonify({'result' : data})

@app.route('/terrain_create/', methods=['GET','POST','OPTIONS'])
@crossdomain(origin='*')
def add_terrain():
  terrain = Terrain
  name = request.json['name']
  height = request.json['height']
  width = request.json['width']
  t_id = terrain.objects.create(name=name,height=height,width=width)
  output = {'CREATED' : t_id['name'], 'height' : t_id['height'], 'width' : t_id['width']}
  return jsonify({'result' : output})

@app.route('/sensor_create/', methods=['GET','POST','OPTIONS'])
@crossdomain(origin='*')
def sensor_create():
  input_data = request.get_json()
  newSensor = Sensor.objects.create(name=input_data["name"],description=input_data["description"],
                                state="True",terrain_object=input_data["terrain_object"])

  for i in input_data["variable"]:
    print SensorVariable.objects.create(id_sensor=newSensor.id, id_variable=str(i))

  output = {'CREATED' : newSensor}
  return jsonify(output)

@app.route('/getsensordata/', methods=['GET','POST','OPTIONS'])
@crossdomain(origin='*')
def sensorvariable():
  input_data = request.get_json()
  data = []

  for sensor in Sensor.objects(terrain_object = input_data['id_terreno']):
    s_data = {}
    s_data['id'] = str(sensor.id)
    s_data['name'] = sensor.name
    s_data['description'] = sensor.description
    s_data['state'] = sensor.state

    for sensorvariable in SensorVariable.objects(id_sensor = sensor):
      variables = []
      for variable in Variable.objects():
        if str(variable.id) == str(sensorvariable.id_variable.id):
          v_data = {}
          v_data['name'] = str(variable.name)
          v_data['unit'] = str(variable.unit)
          v_data['min_value'] = str(variable.min_value)
          v_data['max_value'] = str(variable.max_value)
          v_data['alert_min'] = str(variable.alert_min)
          v_data['alert_max'] = str(variable.alert_max)
          variables.append(v_data)
    s_data['variables'] = variables
  data.append(s_data)
  return jsonify({'result' : data})

@app.route('/getsdata/', methods=['GET','POST','OPTIONS'])
@crossdomain(origin='*')
def sensordata():
  input_data = request.get_json()
  print input_data['num']
  return jsonify({'result' : Data.objects(sensor_object = input_data['id_sensor'], variable_type=input_data['id_variable'])[:int(input_data['num'])].order_by('-value_timestamp')})

@app.route('/sensoralert/', methods=['GET','POST','OPTIONS'])
@crossdomain(origin='*')
def sensorAlerts():
  input_data = request.get_json()
  print input_data['id_sensor']
  return jsonify({'result' : Alert.objects(sensor_object = input_data['id_sensor']).order_by('value_timestamp')})#value_timestamp__gt = str(datetime.datetime.now()-datetime.timedelta(days=1))):

@app.route('/sensorvariables/', methods=['GET','POST','OPTIONS'])
@crossdomain(origin='*')
def sensorVariables():
  input_data = request.get_json()
  print input_data['id_sensor']
  variables = []
  for sensorvariable in SensorVariable.objects(id_sensor = input_data['id_sensor']): 
      for variable in Variable.objects():
        if str(variable.id) == str(sensorvariable.id_variable.id):
          v_data = {}
          v_data['id'] = str(variable.id)
          v_data['name'] = str(variable.name)
          v_data['unit'] = str(variable.unit)
          v_data['min_value'] = str(variable.min_value)
          v_data['max_value'] = str(variable.max_value)
          v_data['alert_min'] = str(variable.alert_min)
          v_data['alert_max'] = str(variable.alert_max)
          variables.append(v_data)
  return jsonify({"result": variables})


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

