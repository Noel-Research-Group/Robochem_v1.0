"""
Diego Pintossi, Zhenghui Wen
Noël Research Group
Van 't Hoff Institute for Molecular Sciences (HIMS)
Universiteit van Amsterdam (UvA)

2021-06-24

Class to control a syringe pump (Chemyx Fusion Series).

Code adapted from the Python program provided by Chemyx at:
https://www.chemyx.com/support/knowledge-base/programming-and-computer-control/python-program-for-chemyx-syringe-pumps/
(last visited June 29, 2021)

"""

import serial
import time
import asyncio
from Logging_organizer.Logging_Setting import setup_logger
from List_connected_devices import find_port


class SyringePump:
    """
    Gives the user control over a syringe pump (Chemyx Fusion series)

    :param port: str
        Name of the CSV file
    :param baudrate: int
        Baudrate for the serial connection. 9600 for RS-232. 38400 for USB.
    :param name: str
        Name of the device. Used in logging.
    :param mode: int
        No idea what this actually does. Default value is good.
    :param x: int
        No idea what this actually does. Default value is good.
    """
    def __init__(self, port, baudrate, name, mode=0, x=0):
        self.logger = setup_logger(f'{name}_logger', f'{name}.log')

        self.logger.info(f"Device is initialized.")

        self.name = name
        self.logger.info(f"Devices name: {name}")
        self.port = port
        self.logger.info(f"Port: {port}")

        # Create a serial port connection with the device
        self.serialObj = serial.Serial()
        self.serialObj.timeout = 0
        self.serialObj.baudrate = baudrate
        self.serialObj.parity = serial.PARITY_NONE
        self.serialObj.stopbits = serial.STOPBITS_ONE
        self.serialObj.port = port
        # Open connection
        try:
            self.serialObj.open()
            self.logger.info(f"Open serial port {self.serialObj.name}")
        except serial.SerialException as error:
            self.logger.error(error)
            self.logger.warning(
                f"Connection to serial port {self.serialObj.name} FAILED")

        self.device_type = "syringe_pump"

        self.verbose = False  # this is just to print stuff or not
        self.mode = mode  # should be 0 for basic operation
        self.x = x

    def open_connection(self):
        """ Function to establish serial connection to the syringe pump.
        """
        try:
            self.serialObj.open()
            if self.verbose:
                print(f"Opened port{self.port}")
                print(self.serialObj)
            self.logger.info(f"Opened port{self.port}.")
            # self.get_pump_status()
            self.serialObj.flushInput()
            self.serialObj.flushOutput()
        except serial.SerialException as error:
            if not self.serialObj.isOpen():  # no error with already open
                if self.verbose:
                    print('Failed to connect to pump')
                    print(error)
                self.logger.warning("Failed to connect to pump.")

    def close_connection(self):
        """ Function to terminate the serial connection to the syringe pump.
        """
        self.serialObj.close()
        if self.verbose:
            print("Closed connection")
        self.logger.info("Closed connection")

    def get_response(self):
        """ Function to read pump response to user command.
        """
        try:
            response_list = []
            response = self.serialObj.readlines()
            for line in response:
                line = line.strip(b'\n').decode('utf8')
                line = line.strip('\r')
                if self.verbose:
                    print(line)
                response_list.append(line)
            return response_list
        except TypeError as error:
            if self.verbose:
                print(error)
            self.close_connection()
        except Exception as f:
            if self.verbose:
                print(f)
            self.close_connection()

    def send_command(self, command):
        """ Function to send commands to the syringe pump.

        :param command: string
            command keyword
        """
        try:
            arg = bytes(str(command), 'utf8') + b'\r'
            self.serialObj.write(arg)
            time.sleep(0.3)
            self.logger.info(f"Command '{command}' sent to {self.name}.")
            return self.get_response()
        except TypeError as error:
            if self.verbose:
                print(error)
            self.logger.warning("Failed to send command.")
            self.serialObj.close()

    def add_mode(self, command):
        """ ???

        :param command: string
            command keyword
        """
        if self.mode == 0:
            return command
        else:
            return command + ' ' + str(self.mode - 1)

    def add_x(self, command):
        """ ???

        :param command: (string)
            command keyword
        """
        if self.x == 0:
            return command
        else:
            return str(self.x) + ' ' + command

    def start_pump(self):
        """ Function to start the pump.

        :returns: list
            instrument response
        """
        command = 'start'
        command = self.add_x(command)
        command = self.add_mode(command)
        response = self.send_command(command)
        self.logger.info(f"Pump {self.name} started.")
        return response

    def stop_pump(self):
        """ Function to stop the pump.

        :returns: list
            instrument response
        """
        command = 'stop'
        command = self.add_x(command)
        response = self.send_command(command)
        self.logger.info(f"Pump {self.name} stopped.")
        return response

    def pause_pump(self):
        """ Function to pause the pump.

        :returns: list
            instrument response
        """
        command = 'pause'
        command = self.add_x(command)
        response = self.send_command(command)
        self.logger.info(f"Pump {self.name} paused.")
        return response

    def restart_pump(self):
        """ Function to re-start the pump.

        Returns: list
            instrument response
        """
        command = 'restart'
        return self.send_command(command)

    def set_units(self, units):
        """ Function to set the unit for the flow_rate (and volume)

        :param units: string
            measurement unit keyword

        :returns: list
            instrument response
        """
        units_dict = {'mL/min': '0',
                      'mL/hr': '1',
                      'μL/min': '2',
                      'μL/hr': '3'}
        command = 'set units ' + str(units_dict[units])
        return self.send_command(command)

    def set_diameter(self, diameter):
        """Function to set the syringe diameter (internal) [mm].

        :param diameter: float
            internal diameter of the syringe [mm]

        :returns: list
            instrument response
        """
        command = 'set diameter ' + str(diameter)
        return self.send_command(command)

    def set_rate(self, flow_rate):
        """Function to set the flow_rate.

        :param flow_rate: float
            flow rate used to dispense/withdraw liquid
            (the unit is defined by set_units())

        :returns: list
            instrument response
        """
        time.sleep(0.2)
        command = 'set rate ' + str(flow_rate)
        return self.send_command(command)

    def set_volume(self, volume):
        """Function to set the volume to deliver or withdraw.

        :param volume: float
            volume to be dispensed/withdrawn
            (the unit is defined by set_units())
            volume > 0 == dispense
            volume < 0 == withdraw

        :returns: list
            instrument response
        """
        command = 'set volume ' + str(volume)
        return self.send_command(command)

    def set_delay(self, delay):
        """Function to set the time delay [min] to start delivering
        or withdrawing.

        :param delay: float
            time delay

        :returns: list
            instrument response
        """
        command = 'set delay ' + str(delay)
        return self.send_command(command)

    def set_time(self, timer):
        """Function to set the dispensing time to deliver or withdraw
        the desired volume (flow rate will be adjusted accordingly).

        :param timer: float
            time delay

        :returns: list
            instrument response
        """
        command = 'set time ' + str(timer)
        return self.send_command(command)

    def get_parameter_limits(self):
        """Function to read the volume and flow rate limits allowed by the used
        syringe. Dependent on the syringe diameter setting.
        NOTE: Max volume is usually larger than the real volume of the syringe.

        :returns: list
            instrument response (max rate min rate max volume min volume)
        """
        command = 'read limit parameter'
        return self.send_command(command)

    def get_parameters(self):
        """Function to read the currently set parameters.

        :returns: list
            instrument response
        """
        command = 'view parameter'
        return self.send_command(command)

    def get_displaced_volume(self):
        """Function to read the volume dispensed/withdrawn since the beginning
        of the current (or last) run/step.

        :returns: list
            instrument response
        """
        command = 'dispensed volume'
        return self.send_command(command)

    def get_elapsed_time(self):
        """Function to read the time [min] elapsed since the beginning of the
        current (or last) run/step.

        :returns: list
            instrument response
        """
        command = 'elapsed time'
        return self.send_command(command)

    def get_pump_status(self):
        """Function to read the pump status.

        :returns: list
            instrument response
            0: pump stopped
            1: pump started
            2: pump paused
            3: pump delayed
            4: pump stalled
        """
        command = 'pump status'
        return self.send_command(command)

    def get_help(self):
        """Function to get a list of available commands.

        :returns: list
            instrument response
        """
        command = 'help'
        return self.send_command(command)

    def estimate_time(self, volume, flow_rate):
        """Function to estimate the time required to dispense the desired
        volume at the selected flow rate. The offset is required because
        the time given by volume / flow_rate is too short.

        :param volume: float
            volume [μL], (+) to dispense, (-) to aspirate
        :param flow_rate: float
            flow rate [mL/min]
        :return: float
            estimated time required to dispense the volume [s]
        """
        if volume < 0:
            volume *= -1
        offset = 5.5 if flow_rate > 20 else 3.5
        return offset + 60 * volume / (1000*flow_rate)

    async def operate_pump(self, volume, flow_rate, skip_wait=False):
        """Function to dispense or aspirate fluid.

        :param volume: float
            volume [μL], (+) to dispense, (-) to aspirate
        :param flow_rate: float
            flow rate [mL/min]
        :param skip_wait: bool
            Parameter to avoid waiting for completed execution of pumping
        """
        # self.open_connection()  # try to keep it open to reduce overhead
        await asyncio.sleep(0.1)
        self.set_volume(volume)
        await asyncio.sleep(0.1)
        self.set_rate(1000*flow_rate)
        await asyncio.sleep(0.1)
        self.start_pump()
        if not skip_wait:
            await asyncio.sleep(self.estimate_time(volume, flow_rate))
        else:
            await asyncio.sleep(2)
        self.stop_pump()
        # self.close_connection()

    async def operate_pump_safe(self, volume, flow_rate):
        """Function to:
            - check if volume and flow_rate are within limits
            - dispense or aspirate fluid
            - check execution
            - repeat if it did not work

        :param volume: float
            volume [μL], (+) to dispense, (-) to aspirate
        :param flow_rate: float
            flow rate [mL/min]
        """
        # compare volume and flow_rate with allowed values
        await asyncio.sleep(0.20)
        max_volume = 10000  # we use 10 mL gas-tight syringes
        max_flow_rate = float(self.get_parameter_limits()[1].split(" ")[0])
        if abs(volume) > max_volume:
            volume = max_volume if volume > 0 else (-max_volume)
            self.logger.warning(
                f"Input volume too high. Changed to {max_volume} μL."
            )
        if 1000*flow_rate > max_flow_rate:
            flow_rate = max_flow_rate/1000
            self.logger.warning(
                f"Input flow rate too high. Changed to {max_flow_rate/1000} mL/min."
            )
        # dispense/aspirate volume at desired flow rate
        await asyncio.sleep(0.05)
        self.set_volume(volume)
        await asyncio.sleep(0.05)
        self.set_rate(1000*flow_rate)
        await asyncio.sleep(0.20)
        self.start_pump()
        time.sleep(self.estimate_time(volume, flow_rate))
        self.stop_pump()
        # check it actually happened and re-try if not
        dispensed_vol = float(self.get_displaced_volume()[1].split(" ")[3])
        self.logger.debug(
            f"Required volume: {volume} μL. "
            + f"Displaced volume: {dispensed_vol} μL."
        )
        await asyncio.sleep(0.10)
        pos_neg = -1 if volume < 0 else 1  # set as dispensing/withdrawing
        vol_diff = abs(volume) - dispensed_vol
        if vol_diff > 5:  # 5 μL tolerance
            await asyncio.sleep(0.05)
            self.set_volume(vol_diff * pos_neg)
            await asyncio.sleep(0.05)
            self.set_rate(1000*flow_rate)
            await asyncio.sleep(0.20)
            self.start_pump()
            time.sleep(self.estimate_time(vol_diff, flow_rate))
            self.stop_pump()

if __name__ == '__main__':
    my_pump_c = SyringePump(
        port=find_port('Syringe_pump_C'),
        baudrate=38400,
        name='',
    )
    limits = my_pump_c.get_parameter_limits()

    # max volume
    print(f'Max volume: {float(limits[1].split(" ")[2])}')

    # min volume
    print(f'Min volume: {float(limits[1].split(" ")[3])}')

    # max flow rate
    print(f'Max flow rate: {float(limits[1].split(" ")[0])}')

    # max volume
    print(f'Min flow rate: {float(limits[1].split(" ")[1])}')
