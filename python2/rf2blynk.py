#!/usr/bin/env python
"""
rf2blynk.py v2 JemRF Sensor Interface to Blynk 
---------------------------------------------------------------------------------
 Works conjunction with host at www.Blynk.cc
 Visit https://www.jemrf.com/pages/documentation for full details                                 
																				  
 J. Evans October 2019
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
 WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
 CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                                                       

 Revision History                                                                  
 V1.00 - Release
 V2.00 - Upgraded for new blyklib library
 
 Instructions:
 =============
 
 Serial to Blynk 
 ===============
 Messages received through the serial port from JemRF wireless sensors are transformed
 and sent to the Blynk server using the blynk.virtual_write(ID, Value) function.
 
 
 Device ID Mapping
 ==================
 JemRF sensors can perform multiple functions (e.g. 3 temperature sensors, humidity, door switch, relay control, LED control)
 ) all using the same Device ID of the sensor. The Bylnk widgets need unique ID's therefore it is necessary to
 ensure a unique ID is assigned to each JemRF function. This program uses the following logic to try allocate a
 unique Device ID to each function:
 
 TMPA    - DeviceID
 TMPB    - DeviceID + 10
 TMPC    - DeviceID + 20
 BUTTON  - DeviceID + 30
 ANAA    - DeviceID + 40
 ANAB    - DeviceID + 50
 HUM     - DeviceID + 60
 BATT    - DeviceID + 70
 PA      - DeviceID + 80
 
 The above is not perfect and might overlap with device ID's if you have many JemRF Radio modules deployed. 
 You might need to change your device ID'same  so that the above device ID allocations work, or adjust 
 the code in this program accordingly. 
 
 Relay Support
 ==============
 The Bylnk app allows you to create buttons that can be mapped to JemRF relays. This allows you to 
 remote control relay switches wires to the JemRF radio module (see here for more details:
 https://www.jemrf.com/pages/how-to-use-the-flex-module-for-remote-control) . 
 
 We have added code for two remote switches to this application but you can add more as follows. 
 Below you will see some configuration items for relay switches explained below:
 
 button1=13               - This is the Virtual ID of the Blynk button
 button1RFRelayID=3       - This is the JemRF Device ID of the radio module
 button1RFRelay="A"       - This is the Relay Port. JemRF modules support two relays per device (RELAYA and RELAYB)
 
 If you want to add more than two Blynk buttons then add the following code at the bottom of this application source. 
 Make sure you change the "def v13_...." to the virtual device of the button in Blynk. Also create three new global variables
 (described above) to the new button (e.g. button3=15...). Lastly make susre you modify the below code replaying "button1"
 with "button3" or whatever name you gave to the global variable. 
 
 ##=======================================================================
 # Register virtual pin handler
 @blynk.VIRTUAL_WRITE(button1)
 def v13_write_handler(value):
	 dprint('Current button value: {}'.format(value))
	 if value=="0":
                 #sensorID,         rfPort,   wirelessMessage, wCommand
	 	SwitchRF(button1RFRelayID, button1RFRelay, "RELAY", "ON")
	 else:
	 	SwitchRF(button1RFRelayID, button1RFRelay, "RELAY", "OFF")
 ##=======================================================================
 
 
  -----------------------------------------------------------------------------------
"""

import time
import sys
from threading import Thread
from time import sleep
from rflib import rf2serial
from rflib import fetch_messages
from rflib import getMessage
import rflib
import blynklib
global blynk

#Once you have signed up for the Bylmk App you will receive a token which you insert here
BLYNK_AUTH = ''

#================================================================================================
DEBUG = True
Fahrenheit=False           #Set to True to convert all temperature readings from Celciud to Fahrenheit
AllowExternalControl=True  #This is a security setting. Set to True to allow external control of relays
                           #on the JEMRF modules.  

terminalID=59              #This is for a Blynk terminal widget. All messages will get sent to the terminal widget
                           #that must have an ID of 59.
#================================================================================================


# Remote Control
#===============================================================================================
# Support for two Blynk buttons has been included that you can use to control JemRF relays. 
# See above for how to add more than two buttons.
# Relay button 1 configuration
button1=13           ##This is the Blynk Virtual ID
button1RFRelayID=3   ##This is the JemRF Device ID
button1RFRelay="A"   ##"A" for RELAYA, "B" for RELAYB

button2=14
button2RFRelayID=3
button2RFRelay="B"
#===============================================================================================
                           
blynk = blynklib.Blynk(BLYNK_AUTH)

def dprint(message):
  if (DEBUG):
    print message

def BlynkIO(device_id, value):
  dprint("Processing data : DeviceID="+str(device_id)+",Value="+str(value))
  blynk.virtual_write(str(device_id), value)
  blynk.virtual_write(terminalID, str(device_id)+" - "+str(value)+" - "+time.strftime('%X %x\n'))
    
def ProcessMessage(value, DevId, property):
# Notify the host that there is new data from a sensor (e.g. door open)
  try:

    #Send temperature to host
    if property[0:3]=="TMP":
      if Fahrenheit:
          value = value*1.8+32
          value = round(value,2)

    DevId=int(DevId);
          
    if property=="STATE":
        property=="BUTTON"
    if property=="TMPA":
        DevId=DevId+10
    if property=="TMPB":
        DevId=DevId+20
    if property=="TMPC":
        DevId=DevId+30
    if property=="ANAA":
        DevId=DevId+40
    if property=="ANAB":
        DevId=DevId+50
    if property=="HUM":
        DevId=DevId+60
    if property=="BATT":
        DevId=DevId+70
    if property=="PA":
        DevId=DevId+80
    
    BlynkIO(DevId, value)
        
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
          blynk.run()
      except KeyboardInterrupt:
          rflib.event.set()
          break

def SwitchRF(sensorID, rfPort, wirelessMessage, wCommand):
  global AllowExternalControl
  global transmission_queue
  
  if (AllowExternalControl==False): return
  msg='a{0:02}{1}{2}{3}'.format(sensorID, wirelessMessage, rfPort, wCommand)
  dprint("Transmitting : "+msg)
  rflib.transmission_queue.insert(0,msg) #transmit a message
  
# Register virtual pin handler
@blynk.handle_event('write V13')
def v13_write_handler(pin, value):
  dprint('Current button value: {}'.format(value[0]))
  if value[0]=="0":
    SwitchRF(button1RFRelayID, button1RFRelay, "GPIO", "1")
  else:
    SwitchRF(button1RFRelayID, button1RFRelay, "GPIO", "0")


@blynk.handle_event('write V14')
def v14_write_handler(pin,value):
	dprint('Current button value: {}'.format(value[0]))
	if value[0]=="0":
		SwitchRF(button2RFRelayID, button2RFRelay, "GPIO", "1")
	else:
		SwitchRF(button2RFRelayID, button2RFRelay, "GPIO", "0")

#@blynk.VIRTUAL_READ(2)
#def v62_read_handler():
    # This widget will show some time in seconds..
#    blynk.virtual_write(62, "RESET")	
    
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




   
   


