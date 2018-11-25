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

#-----------------------------Clase controladora de alertas para cada mensaje MQTT----------------------------------
class DataHandler(object):

    #Atributo sensor de la clase
    sensor = {}

    #Metodo de inicializacion de la clase DataHandler
    def __init__(self):
        super(DataHandler, self).__init__()


    #Metodo de analisis de pronostico climatico y generacion de recomendacion al usuario basado en datos
    #de reporte del sensor
    #Inputs: Objeto(id_sensor ,id_variable, date, value)
    #Output: Alerta con recomendación preventiva
    def alertsMatch(self, object):

        weather_data = Data.objects(sensor_object= str(object["id_sensor"]),
                                    variable_type= str(object["id_variable"]),
                                    value_timestamp__gt = str(datetime.datetime.strptime(object["date"], "%Y-%m-%dT%H:%M:%S.%f")-datetime.timedelta(days=1)))

        weather_forecast = WeatherData()
        weather_data = weather_data[:100]
        data = round(data/len(weather_data),2)

    #Metodo de busqueda y determinación si la alerta es en la misma hora
    #Inputs: Objeto(id_sensor ,id_variable, date, value)
    #Output: res: Booleano True o False
    def searchSensor(self, object):
        res = False
        #Entra a buscar el flag en tabla de ultima alerta con id_sensor y id_variable
        p_alert = AlertFlag.objects(sensor_object= str(object["id_sensor"]),
                                    variable_object= str(object["id_variable"]),
                                    value_timestamp__gt = str(datetime.datetime.strptime(object["date"], "%Y-%m-%dT%H:%M:%S.%f")-datetime.timedelta(hours=1)))

        #Validacion de si hay Flag de alerta en la tabla y si este flag es mayor a 1 hora,
        #de ser mayor a una hora se realiza la actualizacion del Flag con la informacion nueva sino,
        #no se genera la respuesta (res) la cual crea la alerta para el usuario en la tabla de alertas
        if len(p_alert) > 0:
            if bool(p_alert[0]["alert_flag"]) == True:
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

        #self.alertsMatch(self.sensor)

        #Validacion del valor para generar warning de minimo valor reportado
        if float(object["data"]) <= float(variable.min_value) and float(object["data"]) > float(variable.alert_min):
            print "Alerta warning min_value"
            des = "Alerta warning valor minimo sobre variable: "+ str(variable.name)
            alert_type = "warning"

        #Validacion del valor para generar warning de maximo reportado
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
        search_data = self.searchSensor(self.sensor)
        if (search_data == False):
            print "Entra con flag en:  " + str(search_data)

            #Se genera alerta para guardar en base de datos con los valores entregados por el mensaje MQTT
            Alert(alert_type=alert_type, data=str(str(object["data"])), 
                     description= des,
                     terrain_object= str(Sensor.objects(id=str(object["sensor"]))[0].terrain_object.id), 
                     sensor_object =str(object["sensor"]), 
                     variable_object= str(variable.id),
                     value_timestamp=str(object["date"])).save()


#-------------------------------------------MQTT Methods Handler---------------------------------------------------------
#mqtt.subscribe("System/Sensors/#")

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
