#!/usr/bin/env python
import sys
from threading import Thread
#from bme280 import process_bme_reading
from rflib import rf2serial, fetch_messages, request_reply
import rflib
from time import sleep
import time

def main():
  global response_ind
  try:
      rflib.init()

      #start serial processing thread
      a=Thread(target=rf2serial, args=())
      a.start()

      if (sys.argv[2]=="-V" or sys.argv[2]=="-v"):
        command=sys.argv[1]
      else:
        command='a'+sys.argv[1]+sys.argv[2]
        
      print "SENT     : "+command[1:12]  
      request=request_reply(command) 
      if (request.rt==1):
          for x in range(request.num_replies):
              print "RECEIVED : " + str(request.id[x]) + str(request.message[x])
      else:
          print "NO REPLY"
    
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
