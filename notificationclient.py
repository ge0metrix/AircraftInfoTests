from time import time
import paho.mqtt.client as mqtt
import json
import datetime
import logging
import traceback
import time
import os

logger = logging.getLogger()



def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))
    print(str(mqttc))

def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload) + "\r\n\r\n")
    #data = json.loads(msg.payload.decode('utf8'))
    #notice(data)

def on_PlaneAlert(client, obj, msg):
    try:
        data = json.loads(msg.payload.decode('utf8'))
        logline = "[{}] \t {} \t ALERT!!!! \t {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data.get("ICAO"), data.get("Operator"))
        logger.info(logline)
        print(logline)
    except Exception as e:
        print("Invalid JSON recieved in PlaneAlert: {}\r\n{}".format(msg.payload.decode('utf8'), e))
        pass

def on_PlaneFence(client, obj, msg):
    try:
        topic = str(msg.topic)
        data = json.loads(msg.payload.decode('utf8'))
        if topic == "planefence/notifications":
            #logline = "[{}] \t {} \t ENTERING FENCE \t {}".format(datetime.datetime.now(), data.get("hex"), datetime.datetime.fromtimestamp(data.get("now")))
            logline = "[{}] \t {} \t ENTERING FENCE \t {} \t {} \t {} \t {} \t {}".format(
                datetime.datetime.now(), 
                data.get("hex"), 
                datetime.datetime.fromtimestamp(data.get("now")).strftime("%Y-%m-%d %H:%M:%S"),
                data.get("r"), 
                data.get("t"), 
                0,
                data.get("seenNear").get("display_name")
                )
            #logger.info(logline)
            print(logline)
        if topic == "planefence/endnotifications":
            logline = "[{}] \t {} \t LEAVING FENCE  \t {} \t {} \t {} \t {} \t {}".format(
                datetime.datetime.now(), 
                data.get("hex"), 
                datetime.datetime.strptime(data.get("lastSeen"), '%Y-%m-%d %H:%M:%S.%f').strftime("%Y-%m-%d %H:%M:%S"),
                data.get("r"), 
                data.get("t"), 
                len(data.get("points")),
                data.get("lastSeenNear").get("display_name") 
                )


            #logger.info(logline)
            print(logline)
            #print(json.dumps(data, indent=2, default=str))
    except Exception as e:
        print("Invalid JSON recieved in PlaneFence: {}\r\n".format(msg.payload.decode('utf8')))
        print(traceback.format_exc())
        pass

def on_disconnect(client, obj, msg):
    print("DISCONNECTED")
    mqttc.reconnect()

def on_log(mqttc, obj, level, string):
    
    #print(string)
    pass

MQTTHOST=os.environ.get("MQTTHOST", "127.0.0.1")
MQTTPORT=int(os.environ.get("MQTTPORT", 1883))
print(MQTTHOST, MQTTPORT)
mqttc = mqtt.Client("NotificationClient", clean_session=False)
#mqttc.on_message = on_message
#mqttc.on_log = on_log
mqttc.message_callback_add("planefence/notifications", on_PlaneFence)
mqttc.message_callback_add("planefence/endnotifications", on_PlaneFence)
mqttc.message_callback_add("planealert/notifications", on_PlaneAlert)
mqttc.connect(MQTTHOST, MQTTPORT)
mqttc.on_disconnect = on_disconnect
mqttc.subscribe("#", 0)
mqttc.loop_forever()