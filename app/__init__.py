# -*- encoding: utf-8 -*-
"""
Python Aplication Template
Licence: GPLv3
"""
import os
import sys
import datetime
from flask import Flask
from flask_mongoengine import MongoEngine
from flask_mongorest import MongoRest

from flask_mongorest.views import ResourceView
from flask_mongorest.resources import Resource
from flask_mongorest import operators as ops
from flask_mongorest import methods

from flask import Flask
from flask_mqtt import Mqtt

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../../')))

app = Flask(__name__)

# Esto lo mejor seria traerlo de un archivo de config, pero por ahora lo podemos dejar así
app.config.update(
    DEBUG = True,
    TESTING = True,
    MONGODB_SETTINGS = {
        'HOST': 'localhost',
        'PORT': 27017,
        'DB': 'weatherTasks',
        'TZ_AWARE': False,
    },
)

app.config['MQTT_BROKER_URL'] = 'localhost'  # use the free broker from HIVEMQ
app.config['MQTT_BROKER_PORT'] = 1883  # default port for non-tls connection
app.config['MQTT_USERNAME'] = ''  # set the username here if you need authentication for the broker
app.config['MQTT_PASSWORD'] = ''  # set the password here if the broker demands authentication
app.config['MQTT_KEEPALIVE'] = 5  # set the time interval for sending a ping to the broker to 5 seconds
app.config['MQTT_TLS_ENABLED'] = False  # set TLS to disabled for testing purposes


mqtt = Mqtt(app)
db = MongoEngine(app)
api = MongoRest(app)

from app import views, models
from models import *

#Recorsuces definitions for collections objects 
class TerrainResource(Resource):
    document = Terrain
    #related_resources = {
    #    'content': ContentResource,
    #}
    filters = {
        'name': [ops.Exact, ops.Startswith],
    }
    # rename_fields = {
    #     'author': 'author_id',
    # }

class VariableResource(Resource):
    document = Variable
    filters = {
        'name': [ops.Exact, ops.Startswith],
    }

class SystemParameterResource(Resource):
    document = SystemParameter
    filters = {
        'name': [ops.Exact, ops.Startswith],
    }

class SensorResource(Resource):
    document = Sensor
    filters = {
        'name': [ops.Exact, ops.Startswith],
    }

class DataResource(Resource):
    document = Data
    filters = {
        'name': [ops.Exact, ops.Startswith],
    }

class WeatherDataResource(Resource):
    document = WeatherData
    filters = {
        'name': [ops.Exact, ops.Startswith],
    }

class AlertResource(Resource):
    document = Alert
    filters = {
        'name': [ops.Exact, ops.Startswith],
        'alert_type' : [ops.Exact, ops.Startswith],
    }



#API Registration Methods for REST Operations
@api.register(name='terrain', url='/terrain/')
class TerrainView(ResourceView):
    resource = TerrainResource
    methods = [methods.Create, methods.Update, methods.Fetch, methods.List, methods.Delete]

@api.register(name='variable', url='/variable/')
class VariableView(ResourceView):
    resource = VariableResource
    methods = [methods.Create, methods.Update, methods.Fetch, methods.List, methods.Delete]

@api.register(name='spvariables', url='/spvariables/')
class SPView(ResourceView):
    resource = SystemParameterResource
    methods = [methods.Create, methods.Update, methods.Fetch, methods.List, methods.Delete]

@api.register(name='sensor', url='/sensor/')
class SensorView(ResourceView):
    resource = SensorResource
    methods = [methods.Create, methods.Update, methods.Fetch, methods.List, methods.Delete]

@api.register(name='data', url='/data/')
class DataView(ResourceView):
    resource = DataResource
    methods = [methods.Create, methods.Update, methods.Fetch, methods.List, methods.Delete]

@api.register(name='wdata', url='/wdata/')
class WeatherDataView(ResourceView):
    resource = WeatherDataResource
    methods = [methods.Create, methods.Update, methods.Fetch, methods.List, methods.Delete]

@api.register(name='alert', url='/alert/')
class AlertView(ResourceView):
    resource = AlertResource
    methods = [methods.Create, methods.Update, methods.Fetch, methods.List, methods.Delete]



#MQTT Methods Handler

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('sensor1/temp')

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    print data
    #Store Data from sensor into mongoDB collections
    #data = [str(Sensor.objects(name=str(data["topic"]).split("/")[0])[0].id), str(Variable.objects(name=str(data["topic"]).split("/")[1])[0].id), str(data["payload"])]
    #Data(sensor_object= data[0], variable_type= data[1], data=data[2]).save()
   
