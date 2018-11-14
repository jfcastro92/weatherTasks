# -*- encoding: utf-8 -*-
"""
Python Aplication Template
Licence: GPLv3
"""

from app import db
import datetime
from mongoengine import *

class Terrain(db.Document):
    name = db.StringField(max_length=30, required=True)
    description = db.StringField(max_length=50, required=False)
    height = db.FloatField(required=True)
    width = db.FloatField(required=True)
    lat = db.FloatField(required=True)
    lon = db.FloatField(required=True)


#Variables Data Collection Definitions
class Variable(db.Document):
    name = db.StringField(max_length=30, required=True)
    min_value = db.FloatField()
    max_value = db.FloatField()
    alert_max = db.FloatField()
    alert_min = db.FloatField()
    unit = db.StringField(max_length=5, required=True)

#SystemParameter Data Collection Definitions
class SystemParameter(db.Document):
    name = db.StringField(max_length=30, required=True)
    email = db.StringField(max_length=30, required=True)
    Measure = db.StringField(max_length=30, required=True)
    default = db.StringField(max_length=1, required=True)


#Sensor Data Collection Definitions
class Sensor(db.Document):
    name = db.StringField(max_length=30, required=True, unique=True)
    description = db.StringField(max_length=50, required=False)
    state = db.BooleanField(default=False, required=False)
    terrain_object = db.ReferenceField(Terrain)

#Sensor - Variables Data collection relations
class SensorVariable(db.Document):
    id_sensor = db.ReferenceField(Sensor)
    id_variable = db.ReferenceField(Variable)

#Data Collection Definitions
class Data(db.Document):
    sensor_object = db.ReferenceField(Sensor)
    variable_type = db.ReferenceField(Variable)
    data = db.FloatField(required=True)
    value_timestamp = db.StringField(max_length=100)

#WeatherData Data Collection Definitions
class WeatherData(db.Document):
    temp = db.FloatField(required=True)
    temp_min = db.FloatField(required=True)
    temp_max = db.FloatField(required=True)
    pressure = db.FloatField(required=True)
    humidity = db.FloatField(required=True)
    main = db.StringField(max_length=50, required=True)
    description = db.StringField(max_length=50, required=True)
    clouds = db.StringField(max_length=4, required=True)
    wind = db.FloatField(required=True)
    dt_txt = db.DateTimeField()

#Alert Data Collection Definitions
class Alert(db.Document):
    alert_type = db.StringField(max_length=30, required=True)
    data = db.FloatField(required=True)
    description = db.StringField(max_length=100)
    terrain_object = db.ReferenceField(Terrain)
    sensor_object = db.ReferenceField(Sensor)
    variable_object = db.ReferenceField(Variable)
    value_timestamp = db.StringField(max_length=100)

class AlertFlag(db.Document):
    sensor_object = db.ReferenceField(Sensor)
    variable_object = db.ReferenceField(Variable)
    alert_flag = db.BooleanField(default=False, required=False)
    data = db.FloatField(required=True)
    value_timestamp = db.StringField(max_length=100)

