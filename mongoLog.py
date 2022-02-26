import paho.mqtt.client as mqtt
import json
import pymongo
import urllib
import json
import certifi
import os

def on_message(mqttc, obj, msg):
    pass

def on_PlaneFence(mqttc, obj, msg):
    id = db.planefenceenter.insert_one(json.loads(msg.payload)).inserted_id
    print("saving START of Flight to mongo {} as {}".format( json.loads(msg.payload)["hex"], id))
    pass

def on_PlaneFenceEnd(mqttc, obj, msg):
    id = db.planefence.insert_one(json.loads(msg.payload)).inserted_id
    print("saving END of Flight to mongo {} as {}".format( json.loads(msg.payload)["hex"], id))
    pass

def on_PlaneAlert(mqttc, obj, msg):
    id = db.planealert.insert_one(json.loads(msg.payload)).inserted_id
    print("saving ALERT to mongo {} as {}".format( json.loads(msg.payload)["ICAO"], id))
    pass
def on_message(mqttc, obj, msg):
    pass
    #print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload) + "\r\n\r\n")
    #data = json.loads(msg.payload.decode('utf8'))
    #notice(data)
def on_Point(mqttc, obj, msg):
    id = db.points.insert_one(json.loads(msg.payload)).inserted_id
    print(id)
    pass
    #print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload) + "\r\n\r\n")
    #data = json.loads(msg.payload.decode('utf8'))
    #notice(data)

password = urllib.parse.quote_plus(os.environ.get("MONGOPASS"))
username = os.environ.get("MONGOUSER")
mongohost = os.environ.get("MONGOHOST")
#print(password)
client = pymongo.MongoClient("mongodb+srv://" + username + ":" + password + "@" + mongohost + "/myFirstDatabase?retryWrites=true&w=majority", tlsCAFile=certifi.where())
db = client.planefence

def on_disconnect():
    mqttc.reconnect()



MQTT_HOST:str = os.environ.get("MQTTHOST","127.0.0.1") #Host for MQTT
MQTT_PORT:int = int(os.environ.get("MQTTPORT",1883))
mqttc = mqtt.Client("mongoLog")
mqttc.on_message = on_message
mqttc.on_disconnect = on_disconnect
mqttc.message_callback_add("planefence/notifications", on_PlaneFence)
mqttc.message_callback_add("planefence/endnotifications", on_PlaneFenceEnd)
mqttc.message_callback_add("planealert/notifications", on_PlaneAlert)
mqttc.message_callback_add("planefence/points", on_Point)
mqttc.connect(MQTT_HOST, MQTT_PORT, 60)
mqttc.subscribe("#", 0)
mqttc.loop_forever()