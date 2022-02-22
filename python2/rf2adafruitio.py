#!/usr/bin/env python
"""
rf2adafruitio.py v1 Serial to AdafruitIO
---------------------------------------------------------------------------------
                                                                                  
 J. Evans September 2020
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
 WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
 CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                                                       
                                                                                  
 Revision History                                                                  
 V1.00 - Release
 
"""

import time
import sys
from threading import Thread
from time import sleep
from rflib import rf2serial
from rflib import fetch_messages
from rflib import getMessage
import rflib
from Adafruit_IO import Client, Feed, RequestError

# Set to your Adafruit IO key.
# Remember, your key is a secret,
# so make sure not to publish it when you publish this code!
ADAFRUIT_IO_KEY = ''

# Set to your Adafruit IO username.
# (go to https://accounts.adafruit.com to find your username)
ADAFRUIT_IO_USERNAME = ''

# Create an instance of the REST client
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

#Configurations===============
DEBUG = True
Fahrenheit = True
device_prefix = "rf"
#=============================

def dprint(message):
  if (DEBUG):
    print message

def AdafruiIO(device_id, value, property):
  feed_name=str(device_id.lower())+str(property.lower())
  dprint("Processing data : Feed="+feed_name+",Value="+str(value))
  try: 
      sensor = aio.feeds(feed_name)
  except RequestError: # create a analog feed
      dprint("Creating new feed")
      feed = Feed(name=feed_name)
      sensor = aio.create_feed(feed)

  aio.send(sensor.key, value)
    
def ProcessMessage(value, DevId, property):
# Notify the host that there is new data from a sensor (e.g. door open)
  try:

    DevId=device_prefix+DevId;

    #Send temperature to host
    if property[0:3]=="TMP":
      if Fahrenheit:
          value = value*1.8+32
          value = round(value,2)
          
    #Change STATE to BUTTON so we have one topic for a button sensor
    if property=="STATE":
        property="BUTTON"
    
    AdafruiIO(DevId, value, property)
        
  except Exception as e: dprint(e)
  return(0)

def queue_processing():
  while (True):
    fetch_messages(1);
    while len(rflib.processing_queue)>0:
        message = getMessage();         
        if message.sensordata <> "":
            dprint(time.strftime("%c")+ " " + message.devID+message.data)
            ProcessMessage(float(str(message.sensordata)), message.devID, message.description)
    sleep(0.2)
    if rflib.event.is_set():
          break

def main():
    rflib.init()

    a=Thread(target=rf2serial, args=())
    a.start()
    
    b=Thread(target=queue_processing, args=())
    b.start()
  
    while not rflib.event.is_set():
      try:
          sleep(1)
      except KeyboardInterrupt:
          rflib.event.set()
          break
    
if __name__ == "__main__":
  try:
    main()
  except Exception as e: 
    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
    message = template.format(type(e).__name__, e.args)
    print message
    print e
    rflib.event.set()
  #inally:
    rflib.event.set()
    exit()




   
   


