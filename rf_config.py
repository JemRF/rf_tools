#!/usr/bin/env python
import sys
from threading import Thread
#from bme280 import process_bme_reading
from rflib import rf2serial, fetch_messages
import rflib
from time import sleep
import time

def inbound_message_processing():
  global response_ind
  try:
    while (True):
        sleep(0.2)
        fetch_messages(0);
        while len(rflib.processing_queue)>0:
            response_ind=True
            message = rflib.processing_queue.pop(0)
            print ("RECEIVED : "+message[0]+message[1])
            if len(rflib.processing_queue) == 0:
                rflib.event.set()
                break
        
        if rflib.event.is_set():
            break
  except Exception as e: 
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(e).__name__, e.args)
        print message
        print e
        rflib.event.set()
        exit()

def main():
  global response_ind
  try:
      rflib.init()

      #start serial processing thread
      a=Thread(target=rf2serial, args=())
      a.start()
      
      #start response processing thread
      b=Thread(target=inbound_message_processing, args=())
      b.start()

      if (sys.argv[2]=="-V" or sys.argv[2]=="-v"):
        message=sys.argv[1]
      else:
        message='a'+sys.argv[1]+sys.argv[2]
        
      response_ind=False
      
      rflib.transmission_queue.insert(0,message) #transmit a message
      print "SENT     : "+message[1:12]
      sent_time = time.time()
      while (time.time() - sent_time < 1 and not response_ind):
          sleep(0.001)
      if not response_ind:
          rflib.transmission_queue.insert(0,message) #if no response transmit again one last time
          print "SENT     : "+message[1:12]
      
      start_time = time.time()
      
      while len(rflib.processing_queue)>0:
          sleep(1)
          elapsed_time = time.time() - start_time   
          if (elapsed_time > 3 and response_ind):   
             print "NO RESPONSE"
             rflib.event.set() #exit after 1 second no response
             break
    
  except KeyboardInterrupt:
      rflib.event.set()  #exit

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
