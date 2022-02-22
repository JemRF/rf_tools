#!/usr/bin/env python
from threading import Event

def init():
  global message_queue
  global event
  global rf_event
  message_queue=[]
  event = Event()
  rf_event = Event()
