#!/usr/bin/env python
import time
from time import sleep

class bme280_class: 
  def __init__(self, bme_message, dev_id): 
      self.dev_id=dev_id
      self.temp_rt = 0
      self.press_rt = 0
      self.hum_rt = 0
      self.error = ""
       
      data = [0] * 40
      
      if len(bme_message) <> 40:
        self.error=str(len(bme_message))+" data elements received from the sensor, need 40"
        return
      
      for x in range (0,len(bme_message)):
        data[x] = ord(bme_message[x:x+1]);

      dig_T1 = (data[1] << 8) | data[0];
      dig_T2 = (data[3] << 8) | data[2];
      dig_T3 = (data[5] << 8) | data[4];
      dig_T1 = (data[1] << 8) | data[0];
      dig_T2 = (data[3] << 8) | data[2];
      dig_T3 = (data[5] << 8) | data[4];
      dig_P1 = (data[7] << 8) | data[6];
      dig_P2 = (data[9] << 8) | data[8];
      dig_P3 = (data[11] << 8) | data[10];
      dig_P4 = (data[13] << 8) | data[12];
      dig_P5 = (data[15] << 8) | data[14];
      dig_P6 = (data[17] << 8) | data[16];
      dig_P7 = (data[19] << 8) | data[18];
      dig_P8 = (data[21] << 8) | data[20];
      dig_P9 = (data[23] << 8) | data[22];
      dig_H1 = data[24];
      dig_H2 = (data[26] << 8) | data[25];
      dig_H3 = data[27];
      dig_H4 = (data[28] << 4) | (0x0F & data[29]);
      dig_H5 = (data[30] << 4) | ((data[29] >> 4) & 0x0F);
      dig_H6 = data[31];

      press_raw = (data[32+0] << 12) | (data[32+1] << 4) | (data[32+2] >> 4);
      temp_raw = (data[32+3] << 12) | (data[32+4] << 4) | (data[32+5] >> 4);
      hum_raw  = (data[32+6] << 8) | data[32+7];

      UT = float(temp_raw)
      var1 = (UT / 16384.0 - float(dig_T1) / 1024.0) * float(dig_T2)
      var2 = ((UT / 131072.0 - float(dig_T1) / 8192.0) * (
      UT / 131072.0 - float(dig_T1) / 8192.0)) * float(dig_T3)
      t_fine = int(var1 + var2)
      t = (var1 + var2) / 5120.0
      self.temp = t

      adc = float(hum_raw)
      # print 'Raw humidity = {0:d}'.format (adc)
      h = float(t_fine) - 76800.0
      h = (adc - (float(dig_H4) * 64.0 + float(dig_H5) / 16384.0 * h)) * (
      float(dig_H2) / 65536.0 * (1.0 + float(dig_H6) / 67108864.0 * h * (
      1.0 + float(dig_H3) / 67108864.0 * h)))
      h = h * (1.0 - float(dig_H1) * h / 524288.0)
      if h > 100:
          h = 100
      elif h < 0:
          h = 0
      self.hum = h

      adc = float(press_raw)
      var1 = float(t_fine) / 2.0 - 64000.0
      var2 = var1 * var1 * float(dig_P6) / 32768.0
      var2 = var2 + var1 * float(dig_P5) * 2.0
      var2 = var2 / 4.0 + float(dig_P4) * 65536.0
      var1 = (float(dig_P3) * var1 * var1 / 524288.0 + float(dig_P2) * var1) / 524288.0
      var1 = (1.0 + var1 / 32768.0) * float(dig_P1)
      if var1 == 0:
          self.press_rt=1
      else:
        p = 1048576.0 - adc
        p = ((p - var2 / 4096.0) * 6250.0) / var1
        var1 = float(dig_P9) * p * p / 2147483648.0
        var2 = p * float(dig_P8) / 32768.0
        p = p + (var1 + var2 + float(dig_P7)) / 16.0
        self.press = p
      self.temp_rt = 1
      self.press_rt = 1
      self.hum_rt = 1
      #print time.strftime("%c") + " " + "a"+devid+"TPMA"+str(round(t,2))
      #print time.strftime("%c") + " " + "a"+devid+"HUM"+str(round(h,2))
      #print time.strftime("%c") + " " + "a"+devid+"PA"+str(round(p,1)) 

def process_bme_reading(bme_message, devid):
  return(bme280_class(bme_message, devid))
  
  
  