# Seeed-Studio sensors

___
####Set up the Raspberry Pi
Follow the instructions at:
[Raspberry Pi Setup](https://projects.raspberrypi.org/en/projects/raspberry-pi-setting-up)
___

####Setup of the Grove Base HAT for Raspberry Pi
(summary of the instructions available [here](https://wiki.seeedstudio.com/Grove_Base_Hat_for_Raspberry_Pi/#installation))

Code to install the `Grove Base HAT for Raspberry Pi` (execute in the terminal on Raspberry Pi):
```
# Clone the repository from GitHub
git clone https://github.com/Seeed-Studio/grove.py

# Set current directory to grove.py
cd grove.py

# Python3 installation
sudo pip3 install .
```
**Note:** this step has already been executed on the Raspberry Pi we have.

___

#### Setup of the Oxygen sensor (MIX8410)
(summary of the instructions available [here](https://wiki.seeedstudio.com/Grove-Gas_Sensor-O2-MIX8410/))

Connect the MIX8410 sensor to the A0 position of the Grove Base HAT using the Grove cable.

Creating the script to read the sensor (execute in the terminal on Raspberry Pi):
```
# Set current directory to grove.py/grove/
cd grove.py/grove/

# Create a new Python file named MIX8410.py
nano MIX8410.py
```
After the second command, the file `MIX8410.py` will open inside the `nano` editor. Fill it with the following code:
```
import time , sys, math
from adc import ADC
 
__all__ = ["GroveMix8410Sensor"]
 
VRefer = 3.3
total = 0
Measuredvout = 0
 
class GroveMix8410:
 
 
 
    def __init__(self, channel):
        self.channel = channel
        self.adc = ADC()
 
    @property
    def Mix8410(self):
        value = self.adc.read(self.channel)
        if value != 0:
            voltage = value*3.3/1024.0
            Mix8410Value = voltage* 0.21 *100/ 2.0
            return Mix8410Value
        else:
            return 0
 
Grove = GroveMix8410
 
def main():
    if len(sys.argv) < 2:
        print('Usage: {} adc_channel'.format(sys.argv[0]))
        sys.exit(1)
 
    sensor = GroveMix8410(int(sys.argv[1]))
    print('Detecting 02 value...')
 
    while True:
        print('Mix8410 Value: {0}'.format(sensor.Mix8410))
        time.sleep(1)
 
if __name__ == '__main__':
    main()  
```
To save the script, press `ctrl + O`.
To leave the `nano` editor, press `ctrl + X`.

**Note:** these steps have already been executed on the Raspberry Pi we have.

___

#### Reading of the Oxygen sensor (MIX8410)
In the Raspberry Pi terminal (`grove.py/grove/` should be the current directory):
```
python MIX8410.py 0
```

___

#### Setup of the Temperature and Humidity sensor (AHT20)
(summary of the instructions available [here](https://wiki.seeedstudio.com/Grove-AHT20-I2C-Industrial-Grade-Temperature%26Humidity-Sensor/))

Connect the AHT20 sensor to an I2C position of the Grove Base HAT using the Grove cable.

Done! The script to read the sensor is already available in the cloned folder.

___

#### Reading of the Temperature and Humidity sensor (AHT20)
In the Raspberry Pi terminal (`grove.py/grove/` should be the current directory):
```
python grove_temperature_humidity_aht20.py 0
```
