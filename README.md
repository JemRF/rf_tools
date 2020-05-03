# rf_tools

## Download the repository:
```
git clone https://github.com/JemRF/rf_tools.git
```

## Instructions to load new firmware on JemRF modules
Be careful because this can brick your devide if performed incorrectly!

### 1. Upload new firmware to JemRF Flex Module 
(https://www.jemrf.com/collections/rf-sensors/products/flex-rf-module)
```
cd rf_tools/jemrf-fw
make all
```
### 2. Before uploading new firmware configure Flex Module over the air:
 - Awake (rf_config.py 03 WAKE) - (AWAKE for version 2 and below)
 - Type 2 (rf_config.py 03 TYPE2)

### 3. Connect the Flex Module to the MCU
Raspberry Pi Pinouts:
```
Pin 1 Rpi       - Pin 1 Flex
Pin 6 Rpi       - Pin 10 Flex
Pin 8 Rpi (tx)  - Pin 16 Flex (rx)
Pin 10 Rpi (rx) - Pin 15 Flex (tx)
```
### 4. Verify Flex is connected OK
 - serial_mon.py 9600
 - Power flex OFF/ON and make sure you see the STARTED message
 
### 5. Run the uploader
```
sudo ./cctl-prog  -d /dev/ttyAMA0 -f jemrf-fwX.X.hex

You should see new firmware being loaded like this:

Waiting 10s for bootloader, reset board now
...Bootloader detected
Erasing page 1
Erasing, programming and verifying page 2
Erasing, programming and verifying page 3
Erasing, programming and verifying page 4
Erasing, programming and verifying page 5
Erasing, programming and verifying page 6
....
```
Replacing "X.X" with the version you want to load

### 6. Disconnect Flex from the MCU and re-attach IoT Gateway
 - Check the version of the module (python rf_config.py 03 VERSION)
 - Set the Type back to the original sensor type (python rf_config.py 03 TYPEX)
 


