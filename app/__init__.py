# -*- encoding: utf-8 -*-
"""
Poryecto de grado: WeatherTasks Version 1.0
Juan Fernando Castro Mesa - Ingenieria Sistemas y Computacion
Pontificia Universidad Javeriana Cali - 2018

"""
import os
import sys
import datetime
import json
from datetime import datetime
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

#Archivo de configuracion de parametros del aplicativo WEATHERTASKS
# with open("app/credentials.txt", "r") as cred:
#     connection_data = []
#     for line in cred:
#         connection_data.append(line.rstrip('\n'))

app = Flask(__name__)

#--------------------------CONFIGURACION DE PARAMETROS DE CONEXION MONGODB Y MQTT----------------------------------
#Se realiza la configuración de la base de datos en donde el aplicativo weatherTasks va a almacenar los datos del
#terreno y todos los mensajes de variables ambientales que se reporten mediante el broker de transmision MQTT.
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

#Se realiza la definicion de la conexion con el broker MQTT, el cual usa MOSQUITTO MQTT para realizar todo el proceso
#de publicacion o suscripcion a los mensajes entre los componentes del sistema (M2M).

app.config['MQTT_BROKER_URL'] =  '162.243.173.22' # IP donde esta el servicio de Broker MQTT
app.config['MQTT_BROKER_PORT'] = 1883  # Puerto conexion al borker MQTT
app.config['MQTT_USERNAME'] = 'weathertasks' # Username de conexion al broker
app.config['MQTT_PASSWORD'] = 'wtasks2018Admin'  # Password de conexion al broker
app.config['MQTT_KEEPALIVE'] = 45  # Intervalo de tiempo de envio de PING al broker
app.config['MQTT_TLS_ENABLED'] = False  # Parametro de seguridad SSL para cifrado de los datos

#-------------------------------------INSTANCIACION DE LOS MODULOS WEATHERTASKS-------------------------------------
#Mediante la declaracion de las variables db, api, mqtt realizamos el encapsulamiento de las librerias necesarias
#como MongoEngine, Mqtt y MongoRest las cuales crean un contexto de aplicacion que da lugar a manejar los datos de
#WEATHERTASKS a nivel de paso de mensajes MQTT, Manejador de colecciones de base de datos MONGODB e interfaces de
#servicios web REST para interactuar con los modelos definidos para el aplicativo.
db = MongoEngine(app)
api = MongoRest(app)
mqtt = Mqtt(app)

from app import views, models
from models import *
from app.dataHandler import DataHandler

#--------------------------------------Declaracion de la API REST----------------------------------------------------
#Mediante la declaracion de la API REST se realiza el encapsulamiento de los modelos de base de datos creados en
#MongoDB para exponerlos mediante servicios web REST a traves de internet y asi realizar la manipulacion de los datos
#Cada entidad del prototipo tiene su modelo de base de datos con su CRUD (Create, Request, Update y Delete). Mediante
#la definicion de las clases manejadoras de cada coleccion de base de datos y las reglas de busqueda en las consultas
#se realiza toda la creacion del modelo de datos del aplicativo WeatherTasks.

class TerrainResource(Resource):
    document = Terrain
    filters = {
        'name': [ops.Exact, ops.Startswith],
    }

class VariableResource(Resource):
    document = Variable
    filters = {
        'name': [ops.Exact, ops.Startswith]
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
        'terrain_object': [ops.Exact]
    }

class SensorVariableResource(Resource):
    document = SensorVariable
    filters = {
        'name': [ops.Exact, ops.Startswith],
        'id_sensor': [ops.Exact],
        'id_variable': [ops.Exact]
    }

class DataResource(Resource):
    document = Data
    filters = {
        'sensor_object': [ops.Exact],
        'variable_type': [ops.Exact]
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
        'terrain_object' : [ops.Exact],
        'sensor_object' : [ops.Exact],
        'variable_object' : [ops.Exact]
    }

class AlertFlagResource(Resource):
    document = AlertFlag
    filters = {
        'sensor_object' : [ops.Exact],
        'variable_object' : [ops.Exact]
    }


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

@api.register(name='svariable', url='/svariable/')
class SensorVariableView(ResourceView):
    resource = SensorVariableResource
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

api.register(name='alertflag', url='/alertf/')
class AlertFlagView(ResourceView):
    resource = AlertFlagResource
    methods = [methods.Create, methods.Update, methods.Fetch, methods.List, methods.Delete]


#-------------------------------------------MQTT Methods Handler---------------------------------------------------------
mqtt.subscribe("System/Sensors/#")

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print('on_connect client : {} userdata :{} flags :{} rc:{}'.format(client, userdata, flags, rc))

@mqtt.on_disconnect()
def handle_disconnect(client, userdata, rc):
    print('on_disconnect client : {} userdata :{} rc :{}'.format(client, userdata, rc))


@mqtt.on_subscribe()
def handle_subscribe(client, userdata, mid, granted_qos):
    print('on_subscribe client : {} userdata :{} mid :{} granted_qos:{}'.format(client, userdata, mid, granted_qos))

@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    
    #Descodificacion del mensaje JSON y creacion del dato con el mensaje MQTT reportado desde 
    #la estacion de toma de variables mediambientales en el cultivo
    mqtt_data = json.loads(message.payload)
    data = dict(
       sensor=mqtt_data["Sensor_ID"],
       data=mqtt_data["Value"],
       variable = mqtt_data["Variable_ID"],
       date = mqtt_data["Date"]
    )
    print data

    #Almacenamiento de valores de variables medioambientales en la tabla de datos del aplicativo
    if (len(Sensor.objects(id=str(data["sensor"]))) != 0):
        print "Insertando dato :" + str(data["data"])
        Data(sensor_object=str(Sensor.objects(id=str(data["sensor"]))[0].id), 
            variable_type=str(Variable.objects(id=str(data["variable"]))[0].id), 
            data=str(data["data"]), value_timestamp=str(data["date"])).save()

        #Verificacion del dato que llega en el mensaje MQTT para realizar la generacion de la alerta o no
        alertData = DataHandler()
        alertData.alertGenerator(data)
