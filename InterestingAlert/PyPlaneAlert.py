import csv
import json
import datetime
import socket
import paho.mqtt.client as mqtt

"""
CONFIG
"""

minrange = 50.0 #Fence Range
max_alt = 100000 #Fence Altitude
home = (42.52, -71.42) #Fence center

HOST = "10.0.0.229" #Tar1090 Host
PORT = 30047 #Tar1090 Port

MQTT_HOST = "10.0.0.229" #Host for MQTT
MQTT_PORT = 1883
RAISE_NOTICE = True #Publish messages to MQTT?


"""
GLOBALS
"""
alertlist = {}
alerted = {}

def populate_alerlist():
    with open('/Users/abrenden/Downloads/plane-alert-db.csv', mode='r') as infile:
        header = infile.readline()
        keys = header.split(',')
        new_keys = []
        for key in keys:
            new_keys.append(key.replace("#","").replace("$","").replace(" ","_").replace("\n",""))
        reader = csv.DictReader(infile, fieldnames=new_keys)
        for row in reader:
            alertlist[row["ICAO"].lower()] = row



def check_alert(icao:str):
    if icao.lower() in alertlist:
        return alertlist[icao.lower()]
    return None

def notify(msg):
    if RAISE_NOTICE and MQTT_HOST != "" and MQTT_HOST != None:
        mqttclient = mqtt.Client(client_id="PlaneAlert")
        mqttclient.connect(MQTT_HOST, port=MQTT_PORT, keepalive=60)
        print(json.dumps(msg, default=str))
        mqttclient.publish("planealert/notifications",json.dumps(msg, default=str))
    return


def __main__():
    populate_alerlist()
    i = 0
    lst = datetime.datetime.now()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        f = s.makefile(mode="r",buffering=2048,encoding='ascii')
        while True:
            try:
                line = f.readline()
                if len(line)==0:
                    s.connect((HOST, PORT))
                    continue
                msg = json.loads(line)
                icao = msg["hex"]
                aircraft = check_alert(icao)
                seconds = 0
                now = datetime.datetime.now()
                
                if icao in alerted:
                    last = alerted[icao]
                    
                    dur = now - last
                    seconds  = dur.total_seconds()
                    #print("{} seen at {} - {} seconds since last sighting".format(icao, now, seconds))

                if (aircraft != None):
                    if ( seconds > 300 or seconds == 0 ):
                        #ALERT!
                        aircraft["msg"]=msg
                        notify(aircraft)
                        print(aircraft)
                    alerted[icao] = datetime.datetime.now()

            except Exception as e:
                print(line)
                print(e)
                print("----------------------")
                continue
__main__()