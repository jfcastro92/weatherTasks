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

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../../')))

app = Flask(__name__)

# Esto lo mejor seria traerlo de un archivo de config, pero por ahora lo podemos dejar así
app.config.update(
    DEBUG = True,
    TESTING = True,
    MONGODB_SETTINGS = {
        'HOST': 'localhost',
        'PORT': 27017,
        'DB': 'test',
        'TZ_AWARE': False,
    },
)


db = MongoEngine(app)
api = MongoRest(app)

from app import views, models
