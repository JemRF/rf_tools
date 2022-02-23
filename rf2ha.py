#!/usr/bin/env python
"""
rf2ha.py v3 Remote control example using Home Assistant to automatically control Christmas lights

 - Set up an automation in Home Assistance to switch lights on/off depending on daylight
 - Switch lights on/off from the dashboard

 Visit https://www.jemrf.com/pages/documentation for full details

 J. Evans October 2020
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
 WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

 Revision History
 V1.00 - Release
 V3.00 - Updated for Python 3

 Instructions:
 =============
 - Build a remote switch using the JemRF Flex module: https://www.jemrf.com/pages/how-to-use-the-flex-module-for-remote-control
 - Install MQTT : sudo pip install paho-mqtt
                  https://jemrf.github.io/RF-Documentation/hass.html
 - Configure the IP address of the MQTT server in the code below (mqtt_server = "127.0.0.1").
 - Configure your Flex module to id "O5", or change all "05" ID's below to your Flex Module ID
 - Configure the Flex module to Type 7 (relay) and reboot (or power the Flex module off/on)
 - Configure a switch in Home Assistant:
    - Using the File Editor Add-On (if not installed in Home assistant use the Supervisor-> Add On Store option)
    - Edit /config/configuration.yaml
    - Add the following section:

switch:
  - platform: mqtt
    name: christmas_lights
    state_topic: "lights/christmas"
    command_topic: "lights/christmas/set"
    value_template: '{{ value_json.state }}'
    payload_on: '{"state":"ON"}'
    payload_off: '{"state":"OFF"}'
    state_on: "ON"
    state_off: "OFF"
    optimistic: false
    retain: true
    qos: 0

    - Restart Home Assistant
    - Run rf2ha.py
    - Using the switch on the dashboard check to see if the remote switch is working
    - Create Sunset and Sunrise automations (Configurations -> Automations)
       - Trigger Type -> Sun
       - Event -> Sunrise
       - Action Tye -> Call Service
       - Service -> MQTT
       - Service data:
         topic: lights/christmas/set
         payload: '{"state":"OFF"}'
       - Repeat above to add a Sunset Automation changing the Event to Sunset and the state":"ON"

Code Explanation:
==================
 - The on_message function handles incoming messages from topic lights/christmas/set instructing the code to switch the lights on or off
 - After the lights switch on/off then this code requests the state of the remote relay using a request_reply call
 - Then the switch status is published back to Home Assistant on the lights/christmas topic so the new switch status can be set in Home Assistant
"""

import time
import sys
from threading import Thread
from time import sleep
from rflib import rf2serial
from rflib import fetch_messages
from rflib import getMessage
import rflib
import paho.mqtt.client as paho
import json

mqtt_server = "127.0.0.1"

#Configurations===============
DEBUG = True
retries = 4 #The number of times to retry if no response received from the remote relay switch
action = ""
#=============================

def dprint(message):
  if (DEBUG):
    print (message)

def queue_processing():
  while (True):
    message = getMessage();
    if message.sensordata != "":
        dprint(time.strftime("%c")+ " " +
        message.devID+message.data + " " +
        str(message.type) + " " +
        message.description + " " +
        str(message.sensordata))
        #Call your code here
    sleep(0.2)
    if rflib.event.is_set():
          break

def on_message(mosq, obj, msg):
    global action
    print(str(msg.payload))
    j=json.loads(msg.payload)
    if j["state"]=="ON" or j["state"]=="OFF":
        action = str(j["state"])

def mqtt_loop():
    global action
    global retries
    mqttc = paho.Client("rf2ha_client")
    mqttc.on_message = on_message
    mqttc.connect(mqtt_server, 1883, 60)
    mqttc.subscribe("lights/christmas/set", 0)

    while (True):
        mqttc.loop()
        if (action!=""):
            mqttc.publish("lights/christmas", action)  #send pre-emptive status
            resend=0
            while (resend<retries):
                rflib.transmission_queue.insert(0,"a05RELAYA"+action) #transmit a message
                sleep(1)
                request=rflib.request_reply("a05RELAYA")
                if (request.rt==1):
                  for x in range(request.num_replies):
                      print("RECEIVED : " + str(request.id[x]) + str(request.message[x]))
                      if str(request.id[x]) + str(request.message[x]).strip("-") == "05RELAYA"+action:
                          resend=99
                      else:
                          resend=resend+1
                else:
                    resend=resend+1
            if (resend>=retries and resend<99):
                if (action=="ON"):
                    mqttc.publish("lights/christmas", "OFF") # set the state back to `off` because the transmission was unsuccessful
                if (action=="OFF"):
                    mqttc.publish("lights/christmas", "ON") # set the state back to `on` because the transmission was unsuccessful
            action=""

        if rflib.event.is_set():
            break

def main():
    rflib.init()

    a=Thread(target=rf2serial, args=())
    a.start()

    c=Thread(target=mqtt_loop, args=())
    c.start()

    while not rflib.event.is_set():
      try:
          sleep(.1)
      except KeyboardInterrupt:
          rflib.event.set()
          break

if __name__ == "__main__":
  try:
    main()
  except Exception as e:
    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
    message = template.format(type(e).__name__, e.args)
    print (message)
    print (e)
    rflib.event.set()
  finally:
    rflib.event.set()
    exit()








