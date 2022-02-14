import socket
import json
from geopy import distance
from geopy.geocoders import Nominatim
import datetime
import paho.mqtt.client as mqtt

minrange = 50.0
max_alt = 100000
HOST = "10.0.0.229"
PORT = 30047
home = (42.52690, -71.42418)
flightlimit = 300
MQTT_HOST = "10.0.0.229"
RAISE_NOTICE = True




seen = {}
mqttclient = mqtt.Client()



def process_msg(msg: dict):
    msg["fence"] = 0
    
    planeloc = (msg["lat"], msg["lon"])
    
    dist = distance.distance(home, planeloc)
    
    if (dist.miles <= minrange) and (msg["alt_geom"] <= max_alt):
        flightnum = get_flightnum(msg["hex"])
    
        msg["fence"] = 1
    
        if not (is_seen_before(msg["hex"], flightnum)):
            if not msg["hex"] in seen:
                seen[msg["hex"]] = []
            seen[msg["hex"]].insert(flightnum, msg)
            seen[msg["hex"]][flightnum]["firstseen"] = datetime.datetime.now()    
            #seen[msg["hex"]][flightnum]["firstseenear"] = get_geocode(msg["lat"], msg["lon"])
            msg["notify"] = 1
        seen[msg["hex"]][flightnum]["lastseen"] = datetime.datetime.now()
    
        if not "points" in seen[msg["hex"]][flightnum]:
            seen[msg["hex"]][flightnum]["points"]=[]
    
        datapoint = { 'lat': msg["lat"], 'lon': msg["lon"], 'alt': msg["alt_geom"], 'now': msg["now"] }
        seen[msg["hex"]][flightnum]["points"].append(datapoint)
        seen[msg["hex"]][flightnum]["NumPoints"] = len(seen[msg["hex"]][flightnum]["points"])
        #print("IN RANGE", msg["hex"], msg["now"] ,msg["lat"], msg["lon"], dist.mi, msg["alt_geom"],  msg["fence"], seen[msg["hex"]][flightnum]["NumPoints"])
    else:
        pass
        #print("OUT OF RANGE", msg["hex"], msg["now"] ,msg["lat"], msg["lon"], dist.mi, msg["alt_geom"],  msg["fence"])
    #return msg

def is_seen_before(msghex: str, flightnum: int) -> bool:
    if msghex in seen:
        last_seen: datetime = seen[msghex][flightnum]["lastseen"]
        now: datetime = datetime.datetime.now()
        dur: datetime.timedelta = now - last_seen
        seconds = dur.total_seconds()
        if seconds <= flightlimit:
            return True
    return False


def get_flightnum(msghex: str) -> int:
    if(is_seen_before(msghex, 0)):
        return len(seen[msghex])-1
    return 0

def startmqtt():
    if RAISE_NOTICE and MQTT_HOST != "" and MQTT_HOST != None:
        mqttclient.on_log = on_log
        mqttclient.connect(MQTT_HOST, keepalive=60)

def get_geocode(lat, lon):
    geolocator = Nominatim(user_agent="planefencepytest")
    geolocator.timeout = 30
    location = geolocator.reverse("{}, {}".format(lat,lon))
    print(location.raw)
    return location.raw

def notify_start(msg):
    if RAISE_NOTICE and MQTT_HOST != "" and MQTT_HOST != None:
        startmqtt()
        print("Alerting Start {}".format(msg["hex"]))
        mqttclient.publish("planefence/notifications",json.dumps(msg, default=str))
        mqttclient.disconnect()
    return

def notify_end(msg):
    if RAISE_NOTICE and MQTT_HOST != "" and MQTT_HOST != None:
        startmqtt()
        print("Alerting End {}".format(msg[-1]["hex"]))
        mqttclient.publish("planefence/endnotifications",json.dumps(msg, default=str))
        mqttclient.disconnect()
    return

def expireflights():
    for icao in seen:
        if seen.get(icao)[-1].get("lastseen") < (datetime.datetime.now() - datetime.timedelta(seconds=flightlimit)) and seen.get(icao)[-1].get("ended") != 1:
            notify_end(seen.get(icao))
            seen.get(icao)[-1]["ended"]=1
    return


def on_log(mqttc, obj, level, string):
    print(string)

def __main__():
    i = 0
    lst = datetime.datetime.now()
    
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
            if "notify" in msg:
                print(msg.get("hex"),"Alerted")
                notify_start(msg)
            i = i + 1
            if i % 1000 == 0 or (datetime.datetime.now()-lst).seconds >= flightlimit:
                lst=datetime.datetime.now()
                #print(json.dumps(seen, indent=4, default=str))
                filename = "data{}.json".format(datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
                print(filename)
                expireflights()
                #with open(filename, 'w') as jsf:
                #    json.dump(seen, jsf, default=str)



__main__()