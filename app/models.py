# -*- encoding: utf-8 -*-
"""
Python Aplication Template
Licence: GPLv3
"""

from app import db
import datetime
from mongoengine import *

#Terrain Data Collection Definitions
class Terrain(Document):
    name = StringField(max_length=30, required=True)
    description = StringField(max_length=50, required=False)
    height = FloatField(required=True)
    width = FloatField (required=True)


#Variables Data Collection Definitions
class Variable(Document):
    name = StringField(max_length=30, required=True)
    min_value = FloatField()
    max_value = FloatField()
    unit = StringField(max_length=5, required=True)

#SystemParameter Data Collection Definitions
class SystemParameter():
    name = StringField(max_length=30, required=True)

#Sensor Data Collection Definitions
class Sensor(Document):
    name = StringField(max_length=30, required=True, unique=True)
    description = StringField(max_length=50, required=False)
    state = BooleanField(default=False, required=False)
    terrain_object = ReferenceField(Terrain)

#Data Collection Definitions
class Data(Document):
    sensor_object = ReferenceField(Sensor)
    variable_type = ReferenceField(Variable)
    data = FloatField(required=True)
    value_timestamp = DateTimeField(default=datetime.datetime.utcnow)

#WeatherData Data Collection Definitions
class WeatherData(Document):
    value = FloatField(required=True)
    value_timestamp = DateTimeField(default=datetime.datetime.utcnow)
    variable_type = ReferenceField(Variable)

#Alert Data Collection Definitions
class Alert(Document):
    alert_type = StringField(max_length=30, required=True)
    description = StringField(max_length=100)
    terrain_object = ReferenceField(Terrain)
    sensor_object = ReferenceField(Sensor)
