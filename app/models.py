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


#Variables Data Collection Definitions
class Variable(db.Document):
    name = db.StringField(max_length=30, required=True)
    min_value = db.FloatField()
    max_value = db.FloatField()
    unit = db.StringField(max_length=5, required=True)

#SystemParameter Data Collection Definitions
class SystemParameter(db.Document):
    name = db.StringField(max_length=30, required=True)

#Sensor Data Collection Definitions
class Sensor(db.Document):
    name = db.StringField(max_length=30, required=True, unique=True)
    description = db.StringField(max_length=50, required=False)
    state = db.BooleanField(default=False, required=False)
    terrain_object = db.ReferenceField(Terrain)

#Data Collection Definitions
class Data(db.Document):
    sensor_object = db.ReferenceField(Sensor)
    variable_type = db.ReferenceField(Variable)
    data = db.FloatField(required=True)
    value_timestamp = db.DateTimeField(default=datetime.datetime.utcnow)

#WeatherData Data Collection Definitions
class WeatherData(db.Document):
    value = db.FloatField(required=True)
    value_timestamp = db.DateTimeField(default=datetime.datetime.utcnow)
    variable_type = db.ReferenceField(Variable)

#Alert Data Collection Definitions
class Alert(db.Document):
    alert_type = db.StringField(max_length=30, required=True)
    description = db.StringField(max_length=100)
    terrain_object = db.ReferenceField(Terrain)
    sensor_object = db.ReferenceField(Sensor)
