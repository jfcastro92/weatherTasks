#Modules and libraries include
from mongoengine import *
import datetime
from flask import Flask
from flask_mongoengine import MongoEngine
from flask_mongorest import MongoRest
from flask_mongorest.views import ResourceView
from flask_mongorest.resources import Resource
from flask_mongorest import operators as ops
from flask_mongorest import methods
import os


#MONGODB Software Database Connection
app.config.update(
    MONGODB_HOST = 'localhost',
    MONGODB_PORT = 27017,
    MONGODB_DB = 'weatherTasks',
)

db = MongoEngine(app)
api = MongoRest(app)

#Database Models definitions

#Terrain Data Collection Definitions
class Terrain(db.Document):
	name = db.StringField(max_length=30, required=True)
	description = db.StringField(max_length=50, required=False)
	height = db.FloatField(required=True)
	width = db.FloatField (required=True)

class TerrainResource(Resource):
    document = Terrain

#Variables Data Collection Definitions
class Variable(db.Document):
	name = db.StringField(max_length=30, required=True)
	min_value = db.FloatField()
	max_value = db.FloatField()
	unit = db.StringField(max_length=5, required=True)

class VariableResource(Resource):
    document = Variable

#SystemParameter Data Collection Definitions
class SystemParameter():
	name = db.StringField(max_length=30, required=True)

class SystemParameterResource(Resource):
    document = SystemParameter

#Sensor Data Collection Definitions
class Sensor(db.Document):
	name = db.StringField(max_length=30, required=True, unique=True)
	description = db.StringField(max_length=50, required=False)
	state = db.BooleanField(default=False, required=False)
	terrain_object = db.ReferenceField(Terrain)

class SensorResource(Resource):
    document = Sensor

#Data Collection Definitions
class Data(db.Document):
	sensor_object = db.ReferenceField(Sensor)
	variable_type = db.ReferenceField(Variable)
	data = db.FloatField(required=True)
	value_timestamp = db.DateTimeField(default=datetime.datetime.utcnow)

class DataResource(Resource):
    document = Data

#WeatherData Data Collection Definitions
class WeatherData(db.Document):
	value = db.FloatField(required=True)
	value_timestamp = db.DateTimeField(default=datetime.datetime.utcnow)
	variable_type = db.ReferenceField(Variable)

class WeatherDataResource(Resource):
    document = WeatherData

#Alert Data Collection Definitions
class Alert(db.Document):
	alert_type = db.StringField(max_length=30, required=True)
	description = db.StringField(max_length=100)
	terrain_object = db.ReferenceField(Terrain)
	sensor_object = db.ReferenceField(Sensor)

class AlertResource(Resource):
    document = Alert


#Resources Definitions
class TerrainResources(Resource):
    document = Terrain
    related_resources = {
        'content': TerrainResource,
    }
    filters = {
        'name': [ops.Exact, ops.Startswith]
    }

class VariableResources(Resource):
    document = Variable
    related_resources = {
        'content': VariableResource,
    }
    filters = {
        'name': [ops.Exact, ops.Startswith]
    }

class SystemParameterResources(Resource):
    document = SystemParameter
    related_resources = {
        'content': SystemParameterResource,
    }
    filters = {
        'name': [ops.Exact, ops.Startswith]
    }

class SensorResources(Resource):
    document = Sensor
    related_resources = {
        'content': SensorResource,
    }
    filters = {
        'name': [ops.Exact, ops.Startswith]
    }

class DataResources(Resource):
    document = Data
    related_resources = {
        'content': DataResource,
    }
    filters = {
        'name': [ops.Exact, ops.Startswith]
    }

class WeatherDataResources(Resource):
    document = WeatherData
    related_resources = {
        'content': WeatherDataResource,
    }
    filters = {
        'name': [ops.Exact, ops.Startswith]
    }

class AlertResources(Resource):
    document = Alert
    related_resources = {
        'content': AlertResource,
    }
    filters = {
        'name': [ops.Exact, ops.Startswith]
    }

#API REST Definitions for each data collection (CRUD)
@api.register(name='terrain', url='/terrain/')
class TerrainView(ResourceView):
    resource = TerrainResources
    methods = [methods.Create, methods.Update, methods.Fetch, methods.List]

@api.register(name='variable', url='/variable/')
class VariableView(ResourceView):
    resource = VariableResources
    methods = [methods.Create, methods.Update, methods.Fetch, methods.List]

@api.register(name='sysp', url='/sysp/')
class SystemParameterView(ResourceView):
    resource = SystemParameterResources
    methods = [methods.Create, methods.Update, methods.Fetch, methods.List]

@api.register(name='sensor', url='/sensor/')
class SensorView(ResourceView):
    resource = SensorResources
    methods = [methods.Create, methods.Update, methods.Fetch, methods.List]

@api.register(name='data', url='/data/')
class DataView(ResourceView):
    resource = DataResources
    methods = [methods.Create, methods.Update, methods.Fetch, methods.List]

@api.register(name='weatherd', url='/weatherd/')
class DataView(ResourceView):
    resource = WeatherDataResources
    methods = [methods.Create, methods.Update, methods.Fetch, methods.List]

@api.register(name='alert', url='/alert/')
class DataView(ResourceView):
    resource = AlertResources
    methods = [methods.Create, methods.Update, methods.Fetch, methods.List]

