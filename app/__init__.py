# -*- encoding: utf-8 -*-
"""
Python Aplication Template
Licence: GPLv3
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

app.config['MQTT_BROKER_URL'] = '162.243.173.22'  # use the free broker from HIVEMQ
app.config['MQTT_BROKER_PORT'] = 8883  # default port for non-tls connection
app.config['MQTT_USERNAME'] = 'weathertasks'  # set the username here if you need authentication for the broker
app.config['MQTT_PASSWORD'] = 'wtasks2018Admin'  # set the password here if the broker demands authentication
app.config['MQTT_KEEPALIVE'] = 45  # set the time interval for sending a ping to the broker to 5 seconds
app.config['MQTT_TLS_ENABLED'] = False  # set TLS to disabled for testing purposes

db = MongoEngine(app)
api = MongoRest(app)
mqtt = Mqtt(app)

from app import views, models
from models import *

#Resources definitions for collections objects 
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

api.register(name='alert', url='/alert/')
class AlertFlagView(ResourceView):
    resource = AlertFlagResource
    methods = [methods.Create, methods.Update, methods.Fetch, methods.List, methods.Delete]

#------------Clase controladora de alertas para cada mensaje MQTT----------------------------------
class DataHandler(object):

    #Atributo sensor de la clase
    sensor = {}

    #Metodo de inicializacion de la clase DataHandler
    def __init__(self):
        super(DataHandler, self).__init__()

    #Metodo de busqueda y determinación si la alerta es en la misma hora
    #Inputs: Objeto(id_sensor ,id_variable, date, value)
    #Output: res: Booleano True o False
    def searchSensor(self, object):
        res = False
        #Entra a buscar el flag en tabla de ultima alerta con id_sensor y id_variable
        p_alert = AlertFlag.objects(sensor_object= str(object["id_sensor"]),
                                    variable_object= str(object["id_variable"]),
                                    )

        #Se convierten las fechas del objeto de entrada y de la ultima alerta reportada en el mismo formato
        datetime_object = datetime.datetime.strptime(object["date"], "%Y-%m-%dT%H:%M:%S.%f")
        last_date = datetime.datetime.strptime(p_alert[0]["value_timestamp"], "%Y-%m-%dT%H:%M:%S.%f")

        #Validacion de si hay Flag de alerta en la tabla y si este flag es mayor a 1 hora,
        #de ser mayor a una hora se realiza la actualizacion del Flag con la informacion nueva sino,
        #no se genera la respuesta (res) la cual crea la alerta para el usuario en la tabla de alertas
        if len(p_alert) > 0:
            if bool(p_alert[0]["alert_flag"]) == True and (datetime_object - datetime.timedelta(hours=1)) < last_date:
                res = True
        else:
            res = False
            AlertFlag(sensor_object=object["id_sensor"],variable_object=object["id_variable"],
             alert_flag= "True", data=object["value"], value_timestamp=object["date"]).save()
        return res


    #Metodo que genera las alertas para el usuario final, de acuerdo al valor reportado por el sensor 
    #en una variable medioambiental especifica. Cada vez que un sensor reporta, se realiza la validacion
    #Inputs: Objeto: sensor, data, variable, date)
    #Output: N/A
    def alertGenerator(self, object):
        
        #Busqueda de la variable ambiental que se esta reportando mediante el mensaje MQTT
        variable = Variable.objects(id=str(object["variable"]))[0]

        #Declaración de variables para la alerta, de acuerdo al valor reportado y la validacion
        #con los maximos y minimos de la variable que se esta reportando
        des = ""
        alert_type = ""

        #Asignacion de los valores del objeto sensor para cada mensaje MQTT que llega al servidor
        self.sensor["id_sensor"] = str(object["sensor"])
        self.sensor["value"] = str(object["data"])
        self.sensor["date"] = str(object["date"])
        self.sensor["id_variable"] = str(object["variable"])

        #Validacion del valor para generar warning de minimo valor reportado
        if float(object["data"]) <= float(variable.min_value) and float(object["data"]) > float(variable.alert_min):
            print "Alerta warning min_value"
            des = "Alerta warning valor minimo sobre variable: "+ str(variable.name)
            alert_type = "warning"

        #Validacion del valor para generar warning de minimo maximo reportado
        elif float(object["data"]) > float(variable.max_value) and float(object["data"]) > float(variable.alert_max):
            print "Alerta warning max_value"
            des = "Alerta warning valor maximo sobre variable: "+ str(variable.name)
            alert_type = "warning"

        #Validacion del valor para generar danger de minimo valor reportado
        elif float(object["data"]) < float(variable.alert_min):
            print "Alerta danger alert_min"
            des = "Alerta danger valor minimo sobre variable: "+ str(variable.name)
            alert_type = "danger"

        #Validacion del valor para generar danger de maximo valor reportado
        elif float(object["data"]) > float(variable.alert_max):
            print "Alerta danger alert_max"
            des = "Alerta danger valor maximo sobre variable: "+ str(variable.name)
            alert_type = "danger"
        else:
            print "Sensor reportando normalmente valor"

        #Validación de bsuqueda de Flag en la base de datos, para saber si la alerta tiene más de 1 hora
        #NOTA: Dado que las variables medioambientales no cambiar de forma subita, se realiza esta validacion
        #para no generar multiples alertas sobre el mismo comportamiento en el cultivo
        if (self.searchSensor(self.sensor) == False):

            #Se genera alerta para guardar en base de datos con los valores entregados por el mensaje MQTT
            Alert(alert_type=alert_type, data=str(str(object["data"])), 
                     description= des,
                     terrain_object= str(Sensor.objects(id=str(object["sensor"]))[0].terrain_object), 
                     sensor_object =str(object["sensor"]), 
                     variable_object= str(variable.id),
                     value_timestamp=str(object["date"])).save()


#-------------------------------------------MQTT Methods Handler---------------------------------------------------------
mqtt.subscribe("System/Sensors/#")

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print('on_connect client : {} userdata :{} flags :{} rc:{}'.format(client, userdata, flags, rc))


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
   
