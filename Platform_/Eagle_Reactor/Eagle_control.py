"""
:mod.:"Eagle_class" -- API for Eagle reactor control
==============================
  module:: Eagle_class
   :platform: Windows
   :synopsis: Control Signify Eagle Reactor
  module_author:: Zhenghui Wen, Aidan Slattery

(c) 2022 Noel Research Group, University of Amsterdam

This provides a python class for controlling the Signify Eagle Reactor
over a local network. Command implementation is based on the manual
"Ethernet communication Eagle.pdf". Communication between PC and Eagle
reactor is realized via CGI(Common Gateway Interface). A ChromeDriver
is requested to send command via Chrome browser. The ChromeDriver can
be downloaded from https://chromedriver.chromium.org/downloads, based on
the version of browser and the type of operating system.

A manually sign-in of the Signify website website ip found in the sensitive data private file
is required before sending any commands. similarly username and password are found in the sensitive data file
"""

# system imports
import sys
#debugging _purposes
sys.path.append('C:\\Users\\Platform\\code\\RoboChem_auto-optimization-platform\\Platform_')
import os
import webbrowser
from urllib.request import urlopen

import keyboard
import time
from Logging_organizer.Logging_Setting import setup_logger

from phase_sensor_CSV_naming import get_your_abs_project_path
from dotenv import load_dotenv
dotenv_path = os.path.join(get_your_abs_project_path(), 'Sensitive_data.env')
env = load_dotenv(dotenv_path)

class EagleReactor(object):
    """
    API for interfacing with the Signify Eagle Reactor.
    Args:
        name (str): Optional name of the Eagle Reactor
    """

    def __init__(self, name=''):
        self.name = name
        self.device_type = "Eagle_Reactor"
        self.logger = setup_logger('EagleReactor_logger', 'EagleReactor.log')

        # 192.168.0.126 is the IP address of the Dynalite ethernet gateway of PC
        assert env, ValueError('could not load environment of sensitive values')
        self.send_url = os.getenv("EAGLE_CONTROL_SEND_URL")
        self.receive_url = os.getenv("EAGLE_CONTROL_RECEIVE_URL")
        self.area = {2: 'Light', 3: 'Fan'}
        self.light_level = 0

    def send_command(self, area, level, channel=1, fade=0):
        """
        Function to send command to browser to control Eagle Reactor

        :param area:
            int, control area for the reactor, area=2 for Light, area=3 for Fan
        :param level:
            int, range from 0 to 100.
        :param channel:
            (Optional) the channel number of the dali driver (for Eagle there
            is only one channel, default channel = 1)
        :param fade:
            (Optional) the fade time in milliseconds (value range 0 to
             5242710 ms, default value = 0)
        :return:
            None
        """

        if 0 <= level <= 100:
            # make command link with area and level
            command_link = self.send_url + 'a=' + str(area) + '&c=' + str(
                channel) + '&l=' + str(level) + '&f=' + str(fade)

            # send command to Eagle via Chrome browser
            webbrowser.open(command_link, new=0)
            time.sleep(8)
            # pyautogui.hotkey('ctrl', 'w')
            keyboard.send('ctrl+w')
            self.logger.debug(f"The level of the {self.area[area]} has been set"
                              f"to {level} %.")
        else:
            self.logger.warning(
                "The value of level is out of range. Please fill in a value"
                "within the range (0, 100)."
            )

    def receive_level(self, area, channel=1):
        """
        Function to receive level from the Eagle Reactor via Chrome browser

        :param area:
            int, control area for the reactor, area=2 for Light, area=3 for Fan
        :param channel:
            (Optional) the channel number of the dali driver (for Eagle there
            is only one channel, default channel = 1)
        :return:
            Level
        """
        # make command link with area and level
        command_link = self.receive_url + 'a=' + str(area) + '&c=' + str(
            channel)

        web_page = urlopen(command_link)
        html_page = web_page.read().decode("utf-8")
        print(html_page)
        received_message = html_page.find("<body>")
        print(received_message)

        time.sleep(5)

        level = received_message.split('=')[1]
        return level

    def fan_on(self):
        """
        Function to turn on the fan of Eagle with 0 % level
        """
        self.send_command(area=3, level=0)  # 0 % level means 100% on for fan
        self.logger.debug(f"The level of the fan has been set 100% on.")

    def fan_off(self):
        """
        Function to turn off the fan of Eagle with 100 % level
        """
        self.send_command(area=3, level=100)  # 100 % level means off for fan
        self.logger.debug(f"The fan has been turned off.")

    def light_on(self):
        """
        Function to turn on the light of Eagle with 100 % level
        """
        self.fan_on()  # Make sure the fan is on before turning on the light
        time.sleep(2)
        self.send_command(area=2, level=100)  # 100% level means on for light
        self.logger.debug(f"The Light of Eagle has been 100% turned on.")

    def light_off(self):
        """
        Function to turn off the light of Eagle with 0 % level
        """
        self.send_command(area=2, level=0)  # 0% level means off for light
        self.logger.debug(f"The Light of Eagle has been turned off.")

    def light_on_with_level(self, level):
        """
        Function to turn on the light of Eagle with given level

        :param level:
            int, range from 0 to 100.
        """
        self.fan_on()  # Make sure the fan is on before turning on the light
        time.sleep(2)
        self.send_command(area=2, level=level)
        self.logger.debug(f"The intensity of the Light of Eagle has been "
                          f"set on with {level} %.")

    def convert_intensity(self, light_power):
        """
        Function to convert the power of light to level

        :param light_power:
            float, the power of light, range (0, 144), unit [W]
        :return:
            int, level of light, range (0, 100)
        """
        light_level = 0
        if 0 <= light_power <= 144:
            light_level = int((0.007 * light_power) * 100)
            self.logger.debug(f"The intensity of the Light of Eagle has been "
                              f"converted to {light_level} %.")
        else:
            self.logger.warning("The value of light power is out of range. "
                                "Please fill in a value in the range (0, 144).")
            sys.exit()
        return light_level

if __name__ == '__main__':
    Eagle = EagleReactor()
    Eagle.fan_on()
    Eagle.light_on()
    time.sleep(10)
    Eagle.light_off()
    Eagle.fan_off()

