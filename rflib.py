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
  global timer
  global RFDebug
  message_queue=[]
  processing_queue=[]
  transmission_queue=[]
  event = Event()
  rf_event = Event()
  timer=0
  RFDebug=False

def automation(value, devID):
  global transmission_queue
  global timer
  if devID=="82" and value==1:
      transmission_queue.insert(0,"a56RELAYAON-") #transmit a message
      timer = time.time() #sets the timer
      print "Automation 1 triggered" 
  
  if (time.time() - timer > 60 and timer<>0): #if more than 60 seconds has passed since timer was set
      transmission_queue.insert(0,"a56RELAYAOFF-") #transmit a message
      timer=0 #diable the timer
      print "Automation 2 triggered" 
 
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
        #Process outgoing messages (RF tramissions)
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
    global rf_event
    global event
    global RFDebug
    
    x=0
    while rf_event.is_set() and not event.is_set():
        sleep(0.1)
    
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
        sleep(0.7)
        while (rf_event.set()): # allow all BME data to arrive
            sleep(0.2)
        temp_queue=message_queue[:] # take another snap shot of the queue
    
    #remove the items from the queue
    for x in range(0, len(temp_queue)):
        if RFDebug:
            print_debug(message_queue[0])
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
                    if (bme280.temp_rt and bme280.hum_rt and bme280.press_rt):
                      if bme280.error <> "":
                          dprint(bme280.error)
                      else:
                          processing_queue.insert(len(processing_queue), (devID, "TMPA"+str(round(bme280.temp,2))))
                          processing_queue.insert(len(processing_queue), (devID, "HUM"+str(round(bme280.hum,2))))
                          processing_queue.insert(len(processing_queue), (devID, "PA"+str(round(bme280.press/100,1))))
                bme_messages=0;
                bme_data=""
            else:
                y=y+1

    #add all items from the temp_queue to the processing queue
    for x in temp_queue:
        processing_queue.insert(len(processing_queue),x)
    
def print_debug(message):
    print message
    for x in range(0, len(message[1])):
        print(message[1][x],ord(message[1][x]))

class getMessage_class: 
  def __init__(self): 
      self.sensordata=""
      
      fetch_messages(1);
      if len(processing_queue)>0:
          message = processing_queue.pop(0)
          self.devID = message[0]
          data = message[1]
          self.data=data

          if data.startswith('BUTTONON'):
              self.sensordata=0
              self.PEPFunction=26
              self.type=1
              self.description="BUTTON"

          if data.startswith('STATEON'):
              self.sensordata=0
              self.PEPFunction=38
              self.type=2
              self.description="STATE"

          if data.startswith('STATEOFF'):
              self.sensordata=1
              self.PEPFunction=38
              self.type=2
              self.description="STATE"

          if data.startswith('BUTTONOFF'):
              self.sensordata=1
              self.PEPFunction=26
              self.type=1
              self.description="BUTTON"

          if data.startswith('TMPA'):
              self.sensordata=str(data[4:].rstrip("-"))
              self.PEPFunction=37
              self.type=3
              self.description="TMPA"
          
          if data.startswith('ANAA'):
              sdata=str(data[4:].rstrip("-"))
              sdata=(float(sdata)-1470)/16 #convert it to a reading between 1(light) and 48 (dark)
              sdata=str(sdata)
              self.sensordata=sdata
              self.PEPFunction=37
              self.type=4
              self.description="ANAA"
          
          if data.startswith('ANAB'):
              sdata=str(data[4:].rstrip("-"))	
              sdata=(float(sdata)-1470)/16 #convert it to a reading between 1(light) and 48 (dark)
              self.sensordata=str(sdata)
              self.PEPFunction=37
              self.type=10
              self.description="ANAB"
 
          
          if data.startswith('TMPC'):
              self.sensordata=str(data[4:].rstrip("-"))
              self.PEPFunction=37
              self.type=6
              self.description="TMPC"
          
          if data.startswith('TMPB'): 
              self.sensordata=str(data[4:].rstrip("-"))
              self.PEPFunction=37
              self.type=5
              self.description="TMPB"
                                 
          if data.startswith('HUM'):
              self.sensordata=str(data[3:].rstrip("-"))								
              self.PEPFunction=37
              self.type=7
              self.description="HUM"
          
          if data.startswith('PA'):
              self.sensordata=str(data[2:].rstrip("-"))								
              self.PEPFunction=37
              self.type=8
              self.description="PA"
                  
          if data.startswith('BATT'):
              self.sensordata=data[4:].strip('-')
              self.PEPFunction=22
              self.type=9
              self.description="BATT"
              
def getMessage():
    return(getMessage_class())
  
class requestReply_class: 
    def __init__(self, command): 
        self.rt=False
        self.id = []
        self.message = []
        self.num_replies=0
        transmission_queue.insert(0,command) #transmit a message
        overall_time = time.time()
        sent_time = time.time()
        while (not self.rt):
            if (time.time() - overall_time > 4): #timeout after n seconds
                return
            if (time.time() - sent_time > 1.5): #resend after 1.5 seconds if no reply
                transmission_queue.insert(0,command) #re-transmit the message
                sent_time = time.time()
            fetch_messages(0) 
            while (len(processing_queue)): # we have some messages in the queue
                message = processing_queue.pop(0)          
                if message[0]==command[1:3]: #check the ID 
                    self.id.insert(len(self.id),message[0])
                    self.message.insert(len(self.message),message[1])
                    self.rt=True
                    self.num_replies=self.num_replies+1
            sleep(0.1)
    
def request_reply(command):
    return(requestReply_class(command))
          
            
                