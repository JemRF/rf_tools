#!/usr/bin/env python
import serial
import rfsettings
from time import sleep
import time

def rf2serial():
  try:
    port = '/dev/ttyAMA0'
    baud = 9600
    ser = serial.Serial(port=port, baudrate=baud)
    llapMsg=""
    while (True):
        # wait for a moment before doing anything else
        while ser.inWaiting():
          rfsettings.rf_event.set()
          llapMsg += ser.read()
          # check we have the start of a LLAP message
          t=llapMsg.find('a');
          if (t>=0 and len(llapMsg)-t>=12): # we have an llap message
              start_time = time.time()
              rfsettings.message_queue.insert(0,llapMsg[t+1:t+12])
              llapMsg=""
              sleep(0.2)
        if rfsettings.event.is_set():
          break
        rfsettings.rf_event.clear()
        sleep(0.2)
        
  except Exception as e: 
      template = "An exception of type {0} occurred. Arguments:\n{1!r}"
      message = template.format(type(e).__name__, e.args)
      print message
      print e
      rfsettings.event.set()
      exit()
        