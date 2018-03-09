# -*- coding: utf-8 -*-
import os
import sys
import datetime
import flask

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '../../')))

from flask_mongoengine import MongoEngine
# from flask_debugtoolbar import DebugToolbarExtension

app = flask.Flask(__name__)
app.config.from_object(__name__)
app.config['MONGODB_SETTINGS'] = {'DB': 'testing'}
app.config['TESTING'] = True
app.config['SECRET_KEY'] = 'flask+mongoengine=<3'
app.debug = True
#app.config['DEBUG_TB_PANELS'] = (
#    'flask_debugtoolbar.panels.versions.VersionDebugPanel',
#    'flask_debugtoolbar.panels.timer.TimerDebugPanel',
#    'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
#    'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
#    'flask_debugtoolbar.panels.template.TemplateDebugPanel',
#    'flask_debugtoolbar.panels.logger.LoggingPanel',
#    'flask_mongoengine.panels.MongoDebugPanel'
#)

#app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

db = MongoEngine()
db.init_app(app)

# DebugToolbarExtension(app)

#Terrain Data Collection Definitions
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


@app.route('/')
def index():
    # As a list to test debug toolbar
    # Todo.objects().delete()  # Removes
    # Todo(title="Simple todo A ПЫЩЬ!", text="12345678910").save()  # Insert
    # Todo(title="Simple todo B", text="12345678910").save()  # Insert
    # Todo.objects(title__contains="B").update(set__text="Hello world")  # Update
    # todos = Todo.objects.all()
    return 'Hi'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)
