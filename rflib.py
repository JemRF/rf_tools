#!/usr/bin/env python
import serial
from time import sleep
import time
from threading import Event
from bme280 import process_bme_reading

def init():
  global message_queue
  global processing_queue
  global transmission_queue
  global event
  global rf_event
  message_queue=[]
  processing_queue=[]
  transmission_queue=[]
  event = Event()
  rf_event = Event()

def rf2serial():
  global message_queue
  global transmission_queue
  global rf_event
  global event

  try:
    port = '/dev/ttyAMA0'
    baud = 9600
    ser = serial.Serial(port=port, baudrate=baud)
    llapMsg=""
    while (True):
        # wait for a moment before doing anything else
        while ser.inWaiting():
          rf_event.set()
          llapMsg += ser.read()
          # check we have the start of a LLAP message
          t=llapMsg.find('a');
          if (t>=0 and len(llapMsg)-t>=12): # we have an llap message
              start_time = time.time()
              message_queue.insert(len(message_queue),(llapMsg[t+1:t+3], llapMsg[t+3:t+12]))
              llapMsg=""
        if len(transmission_queue)>0:
          ser.write(transmission_queue.pop())
        rf_event.clear()
        if event.is_set():
          break
        sleep(0.1)
        
  except Exception as e: 
      template = "An exception of type {0} occurred. Arguments:\n{1!r}"
      message = template.format(type(e).__name__, e.args)
      print message
      print e
      event.set()
      exit()
      
def fetch_messages(remove_dup_ind): #removed duplicates and converts binary data messages to llap message format
    global message_queue
    global transmission_queue
    global rf_event
    global event
    
    x=0
    while rf_event.is_set() and not event.is_set():
        sleep(1)
    
    if len(message_queue)==0:
        return
    
    sleep(0.3)
    #take a snap shot of the queue because items can be added after sort 
    temp_queue=message_queue[:]
    
    #check for BME sensor data
    found_bme_data=False
    for y in temp_queue:
        if y[1].startswith('BMP'):
            found_bme_data=True
            remove_dup_ind=True
        
    if found_bme_data:
        sleep(1) # allow all BME data to arrive
        temp_queue=message_queue[:] # take another snap shot of the queue
    
    #remove the items from the queue
    for x in range(0, len(temp_queue)):
        message_queue.pop(0)
    
    #sort the queue by ID
    x=0;
    temp_queue = sorted(temp_queue, key = lambda x: (x[0]))
        
    #remove duplicates
    if (remove_dup_ind):
        x=0    
        while x<len(temp_queue)-1:   
            if temp_queue[x][0]==temp_queue[x+1][0] and \
               temp_queue[x][1]==temp_queue[x+1][1]:
                temp_queue.pop(x)
            else:
                x=x+1

    #process BME sensor data
    if found_bme_data:
        y=0
        bme_messages=0
        bme_data=""
        while (y<len(temp_queue)):
            message = temp_queue[y]
            devID = message[0]
            data = message[1]
            if data.startswith('BMP'):
                for x in range (0,5):
                    if y<len(temp_queue):
                        message = temp_queue[y]
                        if message[0]==devID:
                            message = temp_queue.pop(y)
                            if bme_messages==0:
                                bme_data=bme_data+message[1][5:9]
                            else:
                                bme_data=bme_data+message[1][0:9]
                            bme_messages=bme_messages+1
                if bme_messages==5:
                    bme280=process_bme_reading(bme_data, devID)
                    if bme280.error <> "":
                        dprint(bme280.error)
                    else:
                      if bme280.temp_rt == 1:
                          processing_queue.insert(len(processing_queue), (devID, "TMPA"+str(round(bme280.temp,2))))
                      if bme280.hum_rt == 1:
                          processing_queue.insert(len(processing_queue), (devID, "HUM"+str(round(bme280.hum,2))))
                      if bme280.press_rt == 1:
                          processing_queue.insert(len(processing_queue), (devID, "PA"+str(round(bme280.press/100,1))))
                bme_messages=0;
                bme_data=""
            else:
                y=y+1

    #add all items from the temp_queue to the processing queue
    for x in temp_queue:
        processing_queue.insert(len(processing_queue),x)
         
         