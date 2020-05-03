# rf_tools

Download the reportsitory:
```
git clone https://github.com/JemRF/rf_tools.git
```

1. Upload new firmware to JemRF Flex Module
```
cd rf_tools/jemrf-fw
make all
```
2. Before uploading new firmwaer configure Flex Module over the air:
 - Awake (rf_config.py 03 WAKE) - (AWAKE for version 2 and below)
 - Type 2 (rf_config.py 03 TYPE2)

3. Connect the Flex Module to the MCU
Raspberry Pi Pinouts:
```
Pin 1 Rpi       - Pin 1 Flex
Pin 6 Rpi       - Pin 10 Flex
Pin 8 Rpi (tx)  - Pin 16 Flex (rx)
Pin 10 Rpi (rx) - Pin 15 Flex (tx)
```
4. Verify Flex is connected OK
 - serial_mon.py 9600
 - Power flex off/on and make sure you see the STARTED message
 
5. Run the uploader
```
sudo ./cctl-prog  -d /dev/ttyAMA0 -f jemrf-fwX.X.hex
```
Replacing "X.X" with the version you wqant to load


