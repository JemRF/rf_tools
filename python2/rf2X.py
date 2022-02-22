#!/usr/bin/env python

import time
import sys
from threading import Thread
from time import sleep
from rflib import rf2serial
from rflib import fetch_messages
from rflib import getMessage
import rflib

#Configurations===============
DEBUG = True
#=============================

def dprint(message):
  if (DEBUG):
    print message
  
def queue_processing():
  while (True):
    message = getMessage(); 
    if message.sensordata <> "":
        dprint(time.strftime("%c")+ " " + 
        message.devID+message.data + " " + 
        str(message.type) + " " + 
        message.description + " " + 
        str(message.sensordata))
        #Call your code here
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
  finally:
    rflib.event.set()
    exit()




   
   


