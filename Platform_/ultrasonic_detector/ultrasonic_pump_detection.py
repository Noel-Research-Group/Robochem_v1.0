"""
Aidan Slattery
Noël Research Group
Van 't Hoff Institute for Molecular Sciences (HIMS)
Universiteit van Amsterdam (UvA)

Class to receive data from an Arduino UNO running a custom sketch, receiving
a digital input from a HC-SR04 ultrasonic detector. Used to see which carrier
solvent is more full and how much to fill the least full

Connections between board and sensor:

HS04 sensor | Arduino UNO
        yellow wire --> digital pin 12
         blue wire --> digital pin 13
          red wire --> 5V
        black wire --> GND

[!] IMPORTANT NOTE: [!]
Do NOT short the analog wire with GND, as it will lead to constant 0 logical output.

"""

import asyncio
import pandas as pd
import numpy as np
import serial
import time
from List_connected_devices import find_port
from Logging_organizer.Logging_Setting import setup_logger

class UltrasonicDetector:
    """Class to control Ultrasonic detector (HC-SR04 + Arduino
    UNO)"""

    def __init__(self):
        """ Class initialization

        :param device_name: string
            USB port to which the Arduino is connected
        :param sensor_id: integer
            A single number identifying the phase sensor
        :param log_name: string
            name of the log file
        """
        self.logger = setup_logger(f'ultrasonic_logger', f'ultrasonic.log')

        try:
            port = find_port('Pump_A_ultrasonic_detector')
            self.sensor_pump_A = serial.Serial(
                port=port,
                baudrate=9600
            )
            self.logger.info(f'Port: {port}')
            self.logger.info(f'Ultrasonic detector ID: Pump A')
        except serial.SerialException as error:
            self.logger.error(error)
            self.logger.info(f'Connection to ultrasonic detector on Pump A'
                             f'FAILED')

        try:
            port = find_port('Pump_B_ultrasonic_detector')
            self.sensor_pump_B = serial.Serial(
                port=port,
                baudrate=9600
            )
            self.logger.info(f'Port: {port}')
            self.logger.info(f'Ultrasonic detector ID: Pump B')
        except serial.SerialException as error:
            self.logger.error(error)
            self.logger.info(f'Connection to ultrasonic detector on Pump B'
                             f'FAILED')

        try:
            port = find_port('Pump_C_ultrasonic_detector')
            self.sensor_pump_C = serial.Serial(
                port=port,
                baudrate=9600
            )
            self.logger.info(f'Port: {port}')
            self.logger.info(f'Ultrasonic detector ID: Pump C')
        except serial.SerialException as error:
            self.logger.error(error)
            self.logger.info(f'Connection to ultrasonic detector on Pump C'
                             f'FAILED')


    async def get_volume(self, pump):
        """ Conversion of the analog voltage from the phase sensor to the
        corresponding phase (gas < 0.5, liquid > 0.5)
        :param: pump
            Which pump is being accessed A, B or C
        :return: int
            the detected phase
        """
        if pump.lower() in 'a':
            # Empty the buffer to ensure reading of recent values
            # Arduino writing frequency >> Python reading frequency
            self.sensor_pump_A.flushInput()

            # Second attempt to do the calculation if the first one fails
            # (likely buffer issues)
            try:
                # Read 5 values from the buffer (5 x ~100 ms)
                values = [
                        float(self.sensor_pump_A.readline().decode(encoding='ascii'))
                        for _ in range(20)
                ]
                value = np.median(values)
                volume = convert_to_volume_pump_a(value)
            except ValueError:
                # Read 5 values from the buffer (5 x ~100 ms)
                values = [
                    float(self.sensor_pump_A.readline().decode(encoding='ascii'))
                    for _ in range(20)
                ]
                value = np.median(values)
                volume = convert_to_volume_pump_a(value)

        elif pump.lower() in 'b':
            # Empty the buffer to ensure reading of recent values
            # Arduino writing frequency >> Python reading frequency
            self.sensor_pump_B.flushInput()

            # Second attempt to do the calculation if the first one fails
            # (likely buffer issues)
            try:
                # Read 5 values from the buffer (5 x ~100 ms)
                values = [
                    float(
                        self.sensor_pump_B.readline().decode(encoding='ascii'))
                    for _ in range(20)
                ]
                value = np.median(values)
                volume = convert_to_volume_pump_b(value)
            except ValueError:
                # Read 5 values from the buffer (5 x ~100 ms)
                values = [
                    float(
                        self.sensor_pump_B.readline().decode(encoding='ascii'))
                    for _ in range(20)
                ]
                value = np.median(values)
                volume = convert_to_volume_pump_b(value)

        elif pump.lower() in 'c':
            # Empty the buffer to ensure reading of recent values
            # Arduino writing frequency >> Python reading frequency
            self.sensor_pump_C.flushInput()

            # Second attempt to do the calculation if the first one fails
            # (likely buffer issues)
            try:
                # Read 5 values from the buffer (5 x ~100 ms)
                values = [
                    float(
                        self.sensor_pump_C.readline().decode(encoding='ascii'))
                    for _ in range(20)
                ]
                value = np.median(values)
                volume = convert_to_volume_pump_c(value)
            except ValueError:
                # Read 5 values from the buffer (5 x ~100 ms)
                values = [
                    float(
                        self.sensor_pump_C.readline().decode(encoding='ascii'))
                    for _ in range(20)
                ]
                value = np.median(values)
                volume = convert_to_volume_pump_c(value)

        return round(volume, 10)  # round the average value

    def close(self):
        self.sensor_pump_A.close()
        self.sensor_pump_B.close()
        self.sensor_pump_C.close()

async def connect_to_board(port, sensor_id, log_name):
    """ Function to connect to a phase sensor board and start exporting data.

    This function will connect to a board and start exporting the phase
    detected by the phase sensors to corresponding csv file. The name of
    the csv file is given by a time stamp,the name of the board and the
    name of the phase sensor.
    The execution of this function will continue until actively broken.

    :param port: string
        The COM port the board is connected to.
    :param sensor_id: integer
        A single number identifying the phase sensor.
    :param log_name: string
        The name of the phase sensor for log
    :return:
        The phase (0 or 1) is written to the csv file until True loop
        actively broken.
    """
    ultrasonic_detector = UltrasonicDetector()


def convert_to_volume_pump_a(value):
    # algorithm for converting the value obtained to a volume (y = mx + c)
    # from AS003 (y = 0.0274572x - 7.9125325)
    volume = (0.0274572 * value) - 7.9125325
    volume = volume * 1000
    if volume < 0:
        volume = 0
    elif volume > 10000:
        volume = 10000
    return round(volume, 0)


def convert_to_volume_pump_b(value):
    # algorithm for converting the value obtained to a volume (y = mx + c)
    # from AS003 (y = 0.16456500x - 9.6948657)
    volume = (0.16456500 * value) - 9.6948657
    volume = volume*1000
    if volume < 0:
        volume = 0
    elif volume > 10000:
        volume = 10000
    return round(volume, 0)


def convert_to_volume_pump_c(value):
    # algorithm for converting the value obtained to a volume (y = mx + c)
    # from AS003 (y = 0.0707606x - 25.2220271)
    volume = (0.0707606 * value) - 25.2220271
    volume = volume * 1000
    if volume < 0:
        volume = 0
    elif volume > 25000:
        volume = 25000
    return round(volume, 0)


if __name__ == '__main__':
    detectors = UltrasonicDetector()
    # vol_a = asyncio.run(detectors.get_volume(pump='A'))
    # print(vol_a)



    i = 1
    while True:
        vol_a = asyncio.run(detectors.get_volume(pump='A'))
        vol_b = asyncio.run(detectors.get_volume(pump='B'))
        vol_c = asyncio.run(detectors.get_volume(pump='C'))
        print(f'Round: {i}  Pump A: {vol_a} ul  Pump B: {vol_b} ul  Pump C: {vol_c} ul')
        i += 1
