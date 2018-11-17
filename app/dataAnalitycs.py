# -*- encoding: utf-8 -*-
"""
Poryecto de grado: WeatherTasks Version 1.0
Juan Fernando Castro Mesa - Ingenieria Sistemas y Computacion
Pontificia Universidad Javeriana Cali - 2018

"""

import requests
import json
import schedule
import time

class dataAnalytics(object):
	"""docstring for ClassName"""
	def __init__(self):
		super(dataAnalytics, self).__init__()

	def getData(self):
		print "Consultando la API Climatica..."

		#LLAMADO A LA API QUE TRAE INFORMACION DEL CLIMA DE CADA TRES HORA DURANTE LOS SIGUIENTES 5 DIAS
		forecast = requests.get('http://api.openweathermap.org/data/2.5/forecast?q=Cali,co&units=metric&lang=es&APPID=01afdd8f67ab3efb6af3db388dfe4a01')
		data_f = forecast.json()


		##print data_f["list"][0]
		data = []
		headers = {'content-type': 'application/json'}


		# CONTRUYENDO DATOS DE LA API DEL PRONOSTICO CLIMATICO 
		for i in data_f["list"]:
			data_insert = {"temp": str(i["main"]["temp"]),
			"temp_min" : str(i["main"]["temp_min"]),
			"temp_max" : str(i["main"]["temp_max"]),
			"pressure" : str(i["main"]["pressure"]),
			"humidity" : str(i["main"]["humidity"]),
			"main" : str(i["weather"][0]["main"]), 
			"description" : str(i["weather"][0]["description"]),
			"clouds" : str(i["clouds"]["all"]),
			"wind" : str(i["wind"]["speed"]),
			"dt_txt" : str(i["dt_txt"])}
			r = requests.post('http://0.0.0.0:4002/wdata/', data = json.dumps(data_insert), headers=headers)
			#print r.status_code, r.reason

		print "Se ha completado el proceso de construccion de datos"

def weather_job():
	print("Insertando informacion pronostico climatico...")
	data = dataAnalytics()
	data.getData()

weather_job()
# PROGRAMACION DEL JOB DE LLAMADO DE LA INFORMACION CLIMATICA CADA DIA A LA MEDIA NOCHE
schedule.every().hour.do(weather_job)
