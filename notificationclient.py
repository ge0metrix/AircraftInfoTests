
from calendar import day_abbr
import paho.mqtt.client as mqtt
import json
import datetime
import logging
import traceback


logger = logging.getLogger()



def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))

def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload) + "\r\n\r\n")
    #data = json.loads(msg.payload.decode('utf8'))
    #notice(data)

def on_PlaneAlert(client, obj, msg):
    try:
        data = json.loads(msg.payload.decode('utf8'))
        logline = "[{}] \t {} \t ALERT!!!! \t {}".format(datetime.datetime.now(), data.get("ICAO"), data.get("Operator"))
        logger.info(logline)
        print(logline)
    except Exception as e:
        logger.warning("Invalid JSON recieved in PlaneAlert: {}\r\n{}".format(msg.payload.decode('utf8'), e))
        pass

def on_PlaneFence(client, obj, msg):
    try:
        topic = str(msg.topic)
        data = json.loads(msg.payload.decode('utf8'))
        if topic == "planefence/notifications":
            #logline = "[{}] \t {} \t ENTERING FENCE \t {}".format(datetime.datetime.now(), data.get("hex"), datetime.datetime.fromtimestamp(data.get("now")))
            logline = "[{}] \t {} \t ENTERING FENCE \t {} \t {} \t {} \t {}".format(
                datetime.datetime.now(), 
                data.get("hex"), 
                datetime.datetime.fromtimestamp(data.get("now")),
                data.get("r"), 
                data.get("t"), 
                data.get("seenNear").get("address").get("town")
                )
            #logger.info(logline)
            print(logline)
        if topic == "planefence/endnotifications":
            logline = "[{}] \t {} \t LEAVING FENCE \t {} \t {} \t {} \t {}".format(
                datetime.datetime.now(), 
                data.get("hex"), 
                data.get("lastSeen"),
                data.get("r"), 
                data.get("t"), 
                data.get("seenNear").get("address").get("town")
                )


            #logger.info(logline)
            print(logline)
            #print(json.dumps(data, indent=2, default=str))
    except Exception as e:
        logger.warning("Invalid JSON recieved in PlaneFence: {}\r\n".format(msg.payload.decode('utf8')))
        logger.warning(traceback.format_exc())
        pass

mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.message_callback_add("planefence/notifications", on_PlaneFence)
mqttc.message_callback_add("planefence/endnotifications", on_PlaneFence)
mqttc.message_callback_add("planealert/notifications", on_PlaneAlert)
mqttc.connect("10.0.0.229", 1883, 60)
mqttc.subscribe("#", 0)
mqttc.loop_forever()