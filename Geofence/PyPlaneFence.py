import socket
import json
from geopy import distance
from geopy.geocoders import Nominatim
import datetime
import paho.mqtt.client as mqtt


"""
Configuration
"""
minrange = 50.0 #Fence Range
max_alt = 100000 #Fence Altitude
home = (42.52, -71.42) #Fence center
flightlimit = 60 #Time out after last sighting of an aircraft before we start a new flight

HOST = "10.0.0.229" #Tar1090 Host
PORT = 30047 #Tar1090 Port

MQTT_HOST = "10.0.0.229" #Host for MQTT
MQTT_PORT = 1883
RAISE_NOTICE = True #Publish messages to MQTT?

"""
Globals.

I should probably make this all a class and stuff these in as class members.
"""
seen = {}
mqttclient = mqtt.Client()


def process_msg(msg):
    planeloc = (msg.get("lat"), msg.get("lon"))
    dist = distance.distance(home, planeloc).miles
    hex = msg.get("hex")
    notifystart=False
    if (dist <= minrange) and (msg.get("alt_geom",0) <= max_alt):

        if seen.get(hex) == None:
            seen[hex] = msg
            seen[hex]["points"] = []
            notifystart=True
            seen[hex]["seenNear"] = get_geocode(msg.get("lat"),  msg.get("lon"))
            

        seen[hex]["lastSeen"] = datetime.datetime.now()
        datapoint = { 'lat': msg.get("lat"), 'lon': msg.get("lon"), 'alt': msg.get("alt_geom"), 'now': msg.get("now") }
        seen[hex]["points"].append(datapoint)
        if notifystart:
            notify_start(seen[hex])

def get_geocode(lat, lon):
    geolocator = Nominatim(user_agent="planefencepytest")
    geolocator.timeout = 30
    location = geolocator.reverse("{}, {}".format(lat,lon))
    return location.raw

def startmqtt():
    if RAISE_NOTICE and MQTT_HOST != "" and MQTT_HOST != None:
        mqttclient.on_log = on_log
        mqttclient.connect(host=MQTT_HOST, port=MQTT_PORT ,keepalive=60)

def notify_start(msg):
    if RAISE_NOTICE and MQTT_HOST != "" and MQTT_HOST != None:
        startmqtt()
        print("Alerting Start {}".format(msg["hex"]))
        mqttclient.publish("planefence/notifications",json.dumps(msg, default=str))
        mqttclient.disconnect()

def notify_end(msg):
    if RAISE_NOTICE and MQTT_HOST != "" and MQTT_HOST != None:
        startmqtt()
        print("Alerting End {}".format(msg["hex"]))
        mqttclient.publish("planefence/endnotifications",json.dumps(msg, default=str))
        mqttclient.disconnect()

def expireflights():
    ended = []
    for icao in seen:
        print("{} last seen at {}".format(icao, seen.get(icao).get("lastSeen")))
        if seen.get(icao).get("lastSeen") < (datetime.datetime.now() - datetime.timedelta(seconds=flightlimit)) and seen.get(icao).get("ended") != 1:
            ended.append(icao)

    for x in ended:
        tmp = seen.pop(x)
        notify_end(tmp)


def on_log(mqttc, obj, level, string):
    print(string)
#    pass

def __main__():
    i = 0
    lastCleanup = datetime.datetime.now()
    
    startmqtt()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        f = s.makefile(mode="r",buffering=2048,encoding='ascii')
        while True:
            try:
                line = f.readline()
                msg = json.loads(line)
            except Exception as e:
                print(line)
                print(e)
                print("----------------------")
                continue
            process_msg(msg)
            
            if (datetime.datetime.now()-lastCleanup).seconds >= flightlimit:
                lastCleanup=datetime.datetime.now()
                #print(json.dumps(seen, indent=4, default=str))
                print("Cleaning up at {}".format(lastCleanup))
                expireflights()




__main__()