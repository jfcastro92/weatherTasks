
from app.models import *
import requests
import json
import time
import collections

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
    #Output: Alerta con recomendacion preventiva
    def alertsMatch(self, object):

        #LLAMADO A LA API QUE TRAE INFORMACION DEL CLIMA DE CADA TRES HORA DURANTE LOS SIGUIENTES 5 DIAS
        forecast = requests.get('http://api.openweathermap.org/data/2.5/forecast?q=Cali,co&units=metric&lang=es&APPID=01afdd8f67ab3efb6af3db388dfe4a01')
        data_f = forecast.json()
        data = {}

        for i in data_f["list"]:
            data = {
             "main" : str(i["weather"][0]["main"]), 
             "description" : str(i["weather"][0]["description"])}

        return data["description"]

    #Metodo de busqueda y determinacion si la alerta es en la misma hora
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

        #Declaracion de variables para la alerta, de acuerdo al valor reportado y la validacion
        #con los maximos y minimos de la variable que se esta reportando
        des = ""
        alert_type = ""
        alert = True

        #Asignacion de los valores del objeto sensor para cada mensaje MQTT que llega al servidor
        self.sensor["id_sensor"] = str(object["sensor"])
        self.sensor["value"] = str(object["data"])
        self.sensor["date"] = str(object["date"])
        self.sensor["id_variable"] = str(object["variable"])


        #Validacion del valor para generar warning de minimo valor reportado
        if float(object["data"]) < float(variable.min_value) and float(object["data"]) > float(variable.alert_min):
            print "Alerta warning min_value"
            des = "El sensor esta reportando valores bajos de "+ str(variable.name)
            alert_type = "warning"

        #Validacion del valor para generar warning de maximo reportado
        elif float(object["data"]) > float(variable.max_value) and float(object["data"]) < float(variable.alert_max):
            print "Alerta warning max_value"
            des = "El sensor esta reportando valores altos de "+ str(variable.name)
            alert_type = "warning"

        #Validacion del valor para generar danger de minimo valor reportado
        elif float(object["data"]) <= float(variable.alert_min):
            print "Alerta danger alert_min"
            des = "El sensor esta reportando valores por debajo de los limites en la variable "+ str(variable.name)
            alert_type = "danger"

        #Validacion del valor para generar danger de maximo valor reportado
        elif float(object["data"]) >= float(variable.alert_max):
            print "Alerta danger alert_max"
            des = "El sensor esta reportando valores por encima de los limites en la variable"+ str(variable.name)
            alert_type = "danger"
        else:
            alert = False
            print "Sensor reportando normalmente valor"

        #Validacion de bsuqueda de Flag en la base de datos, para saber si la alerta tiene mas de 1 hora
        #NOTA: Dado que las variables medioambientales no cambiar de forma subita, se realiza esta validacion
        #para no generar multiples alertas sobre el mismo comportamiento en el cultivo
        search_data = self.searchSensor(self.sensor)

        if (search_data == False and alert== True):
            print "Entra con flag en:  " + str(search_data)

            forecast_data = self.alertsMatch(self.sensor)

            description = des + ", clima para los proximas 24 horas es de " + forecast_data

            #Se genera alerta para guardar en base de datos con los valores entregados por el mensaje MQTT
            Alert(alert_type=alert_type, data=str(str(object["data"])), 
                     description= description,
                     terrain_object= str(Sensor.objects(id=str(object["sensor"]))[0].terrain_object.id), 
                     sensor_object =str(object["sensor"]), 
                     variable_object= str(variable.id),
                     value_timestamp=str(object["date"])).save()