"""
Diego Pintossi, Aidan Slattery
Noël Research Group
Van 't Hoff Institute for Molecular Sciences (HIMS)
Universiteit van Amsterdam (UvA)

2022-01-14

Class to receive data from an Arduino UNO running a custom sketch, receiving an
analog input from a TT electronics OCB350 phase sensor.

Connections between board and sensor:

OPB350 phase sensor | Arduino UNO
        white wire --> analog pin A1
        green wire --> floating in empty breadboard line (connect to GND for calibration**)
         blue wire --> digital pin 4
       orange wire --> digital pin 7
          red wire --> 5V
        black wire --> GND

[!] IMPORTANT NOTE: [!]
Do NOT short the analog wire with GND, as it will lead to constant 0 logical output.

** = during calibration the sensor should be removed from the capillary
"""

import time
import serial
import numpy as np
import pandas as pd
from List_connected_devices import find_port
from Logging_organizer.Logging_Setting import setup_logger


class PhaseSensor:
    """Class to control phase sensor (TT electronics OCB350 + Arduino UNO)"""

    def __init__(self, device_name, sensor_id, log_name):
        """ Class initialization

        :param device_name: string
            USB port to which the Arduino is connected
        :param sensor_id: integer
            A single number identifying the phase sensor
        :param log_name: string
            name of the log file
        """
        self.logger = setup_logger(f'{log_name}_logger', f'{log_name}.log')

        self.logger.info(f'Port: {device_name}')
        self.logger.info(f'Phase sensor ID: PS{sensor_id + 1}')
        self.sensor_id = sensor_id
        # sensor_id = 0 for PS1, 1 for PS2 etc
        try:
            self.sensor = serial.Serial(
                port=device_name,
                baudrate=19200
            )
        except serial.SerialException as error:
            self.logger.error(error)
            self.logger.info('Connection to phase sensor FAILED')

    def get_phase(self):
        """ Conversion of the analog voltage from the phase sensor to the
        corresponding phase (gas < 0.5, liquid > 0.5)

        :return: int
            the detected phase
        """
        # time.sleep(0.100)  # keep above 100 ms to avoid issues
        # # Second attempt to do the calculation if the first one fails
        # # (likely buffer issues)
        try:
            # Read 5 values from the buffer (5 x ~100 ms)
            values = [
                int(
                    self.sensor.readline().decode(encoding='ascii')
                ) for _ in range(5)
            ]
            value = np.mean(values)
        except ValueError:
            # Read 5 values from the buffer (5 x ~100 ms)
            values = [
                int(
                    self.sensor.readline().decode(encoding='ascii')
                ) for _ in range(5)
            ]
            value = np.mean(values)

        # Empty the buffer to ensure reading of recent values
        # Arduino writing frequency >> Python reading frequency
        self.sensor.flushInput()

        return float(int(value))  # round the average value

    def get_phase_analog(self):
        """ Conversion of the analog voltage from the phase sensor to the
        corresponding phase (gas < 0.5, liquid > 0.5)

        :return: int
            the detected phase
        """
        # time.sleep(0.100)  # keep above 100 ms to avoid issues
        # # Second attempt to do the calculation if the first one fails
        # # (likely buffer issues)
        # try:
        #     # Read 5 values from the buffer (5 x ~100 ms)
        #     values = [
        #         int(
        #             self.sensor.readline().decode(encoding='ascii')
        #         ) for _ in range(5)
        #     ]
        #     value = np.mean(values)
        # except ValueError:
        #     # Read 5 values from the buffer (5 x ~100 ms)
        #     values = [
        #         int(
        #             self.sensor.readline().decode(encoding='ascii')
        #         ) for _ in range(5)
        #     ]
        #     value = np.mean(values)

        # # Empty the buffer to ensure reading of recent values
        # # Arduino writing frequency >> Python reading frequency
        # self.sensor.flushInput()
        #
        # return float(int(value))  # round the average value
        """ Conversion of the analog voltage from the phase sensor to the
                        corresponding phase (gas < 0.5, liquid > 0.5)

                        :return: int
                            the detected phase
                        """
        time.sleep(0.100)  # keep above 100 ms to avoid issues
        if self.sensor_id + 1 == 4:
            try:
                # Read 5 values from the buffer (5 x ~100 ms)
                values = [
                    int(
                        self.sensor.readline().decode(encoding='ascii')
                    ) for _ in range(5)
                ]
                value = np.mean(values)
            except ValueError:
                # Read 5 values from the buffer (5 x ~100 ms)
                values = [
                    int(
                        self.sensor.readline().decode(encoding='ascii')
                    ) for _ in range(5)
                ]
                value = np.mean(values)
            if value < 37 or value > 47:
                value = 1
            else:
                value = 0
        elif self.sensor_id + 1 == 6:
            try:
                # Read 5 values from the buffer (5 x ~100 ms)
                values = [
                    int(
                        self.sensor.readline().decode(encoding='ascii')
                    ) for _ in range(5)
                ]
                value = np.mean(values)
            except ValueError:
                # Read 5 values from the buffer (5 x ~100 ms)
                values = [
                    int(
                        self.sensor.readline().decode(encoding='ascii')
                    ) for _ in range(5)
                ]
                value = np.mean(values)
            if value < 3 or value > 10:
                value = 1
            else:
                value = 0
        elif self.sensor_id + 1 == 7:
            try:
                # Read 5 values from the buffer (5 x ~100 ms)
                values = [
                    int(
                        self.sensor.readline().decode(encoding='ascii')
                    ) for _ in range(5)
                ]
                value = np.mean(values)
            except ValueError:
                # Read 5 values from the buffer (5 x ~100 ms)
                values = [
                    int(
                        self.sensor.readline().decode(encoding='ascii')
                    ) for _ in range(5)
                ]
                value = np.mean(values)
            if value < 29 or value > 36:
                value = 1
            else:
                value = 0
        else:  # sensors pre-irradiation
            # Second attempt to do the calculation if the first one fails
            # (likely buffer issues)
            try:
                # Read 5 values from the buffer (5 x ~100 ms)
                values = [
                    int(
                        self.sensor.readline().decode(encoding='ascii')
                    ) for _ in range(5)
                ]
                value = np.mean(values)
            except ValueError:
                # Read 5 values from the buffer (5 x ~100 ms)
                values = [
                    int(
                        self.sensor.readline().decode(encoding='ascii')
                    ) for _ in range(5)
                ]
                value = np.mean(values)
            # Empty the buffer to ensure reading of recent values
            # Arduino writing frequency >> Python reading frequency
            self.sensor.flushInput()
            # Logic for converting analogue to to a digital value (1 or 0)
            if value < 29 or value > 36:
                value = 1
            else:
                value = 0
        return float(int(value))  # round the average value

    def give_value(self):
        value = self.sensor.readline().decode(encoding='ascii')
        return(value)

    def close(self):
        self.sensor.close()


if __name__ == '__main__':
    # connect to sensor
    # for i in range(1, 8):
    #     sensor = i
    #     ps7 = PhaseSensor(
    #         find_port(f'PS{sensor}'),
    #         6,
    #         f'test_ps{sensor}.log'
    #     )
    #
    #     for i in range(10):
    #         print(f'Cycle {i}')
    #         print(f'PS{sensor} (digital read): {ps7.get_phase()}')
    #         time.sleep(.600)

    # sensor = 4
    # ps = PhaseSensor(
    #     find_port(f'PS{sensor}'),
    #     6,
    #     f'test_ps{sensor}.log'
    # )
    #
    # for i in range(10):
    #     print(f'Cycle {i}: {ps.give_value()}')
    #     time.sleep(0.100)

    ps4 = PhaseSensor(
        find_port(f'PS4'),
        3,
        f'test_ps4.log'
    )

    ps6 = PhaseSensor(
        find_port(f'PS6'),
        5,
        f'test_ps4.log'
    )

    ps7 = PhaseSensor(
        find_port(f'PS7'),
        6,
        f'test_ps4.log'
    )
    day = 'Mon_5162022'
    number = 3
    phase_data_log = pd.DataFrame(columns=['time (s)',
                                           'PS4 analog',
                                           'PS6 analog',
                                           'PS7 analog',
                                           'PS4',
                                           'PS6',
                                           'PS7',])
    phase_data_log.to_csv(f'Phase_gas_data_{day}_{number}.csv', mode='w', header=True,
                          index=False)
    t = 0
    while True:
        ps4_value = ps4.get_phase()
        ps6_value = ps6.get_phase()
        ps7_value = ps7.get_phase()
        phase_data_log = pd.DataFrame(
            {
                'time (s)': [t],
                'PS4': [ps7_value],
                'PS6': [ps7_value],
                'PS7': [ps7_value],
            },
        )
        phase_data_log.to_csv(f'Phase_gas_data_{day}_{number}.csv', mode='a', header=False, index=False)
        time.sleep(1)
        t += 1

