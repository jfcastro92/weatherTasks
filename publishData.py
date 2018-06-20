#====================================================
# Python libraries 
import paho.mqtt.client as mqtt
import random, threading, json
from datetime import datetime
import time

#====================================================
# MQTT Settings 
MQTT_Broker = "162.243.173.22"
MQTT_Port = 8883
MQTT_User = "weathertasks"
MQTT_Pwd = "wtasks2018Admin"
Keep_Alive_Interval = 5


#====================================================

def on_connect(client, userdata, rc):
	if rc != 0:
		pass
		print "Unable to connect to MQTT Broker..."
	else:
		print "Connected with MQTT Broker: " + str(MQTT_Broker)

def on_publish(client, userdata, mid):
	pass
		
def on_disconnect(client, userdata, rc):
	if rc !=0:
		pass
		
mqttc = mqtt.Client()
mqttc.username_pw_set(MQTT_User, MQTT_Pwd)
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.on_publish = on_publish
mqttc.connect(MQTT_Broker, int(MQTT_Port), int(Keep_Alive_Interval))		

		
def publish_To_Topic(topic, message):
	mqttc.publish(topic,message)
	print ("Published: " + str(message) + " " + "on MQTT Topic: " + str(topic))
	print ""


#====================================================
# FAKE SENSOR 
# Dummy code used as Fake Sensor to publish some random values
# to MQTT Broker

def publish_Fake_Sensor_Values_to_MQTT(sensor, toggle):
	
	while True:
		if toggle == "hum":
			#Generacion de dato de humedad
			Humidity_Fake_Value = float("{0:.1f}".format(random.uniform(50, 100)))

			#Publicacion del dato generado al servidor MOSQUITTO
			print "Publishing Humidity Value: " + str(Humidity_Fake_Value) + "..."
			MQTT_Topic_Humidity = str(sensor + "/" + toggle)
			publish_To_Topic (MQTT_Topic_Humidity, Humidity_Fake_Value)

		elif toggle == "temp":
			#Generacion de dato de temperatura
			Temperature_Fake_Value = float("{0:.2f}".format(random.uniform(1, 50)))

			#Publicacion del dato generado al servidor MOSQUITTO
			print "Publishing Temperature Value: " + str(Temperature_Fake_Value) + "..."
			MQTT_Topic_Temperature = str(sensor + "/" + toggle) 
			publish_To_Topic (MQTT_Topic_Temperature, str(Temperature_Fake_Value))
		else:
			Humidity_Fake_Value = float("{0:.2f}".format(random.uniform(50, 100)))
			Temperature_Fake_Value = float("{0:.2f}".format(random.uniform(1, 50)))

			#Generacion de dato de humedad y temperatura
			MQTT_Topic_Humidity = str(sensor + "/" +"temp")
			MQTT_Topic_Temperature = str(sensor + "/" + "hum")

			#Publicacion del dato generado al servidor MOSQUITTO
			print "Publishing Temperature Value: " + str(Temperature_Fake_Value) + "..."
			publish_To_Topic (MQTT_Topic_Temperature, str(Temperature_Fake_Value))
			print "Publishing Humidity Value: " + str(Humidity_Fake_Value) + "..."
			publish_To_Topic (MQTT_Topic_Humidity, str(Humidity_Fake_Value))
		time.sleep(3)


def main():
	s = raw_input("Ingrese el sensor del que se quiere publicar data")
	v = raw_input("Ingrese la variable ambiental que se va a publicar")
	publish_Fake_Sensor_Values_to_MQTT(s, v)

main()