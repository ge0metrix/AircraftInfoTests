# Aircraft Info Expirments
Just a place for me to play with some ideas I have for ADSB and other data feeds related to aircraft.


The initial thought I've been playing with here is decoupling the parsing, processing, and display of aircraft from a service akin to PlaneFence. While also processing in more real time rather than processing on an interval. 

### Geofence
the GeoFence directory contains a Python script that will push an alert to an MQTT Broker when ever an aircraft is detected within a configurable range & altitude of a point. 

### InterestingAlert 
Provides a script that will push an alert to the MQTT Broker on another publication whenever a "Interesting" aircraft is detected. Currently using the list from SportsBadger to define interesting.


### NotificationClient
Is an example client subscribing to the notifications from above. 



### Plans:

Notification Clients to push to twitter, discord etc.
Client to log the messages to some form of DB (Mongo, or maybe SQLLite)
Client to create a front end, may depend on the logging client to provide a persistance layer.


