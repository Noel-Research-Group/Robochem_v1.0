"""Script with code to control the switch valves via the Arduino sketch.

The Arduino board should be loaded with the sketch:
./Phase_sensors/Arduino sketches/switch_pin_output/switch_pin_output.ino

D.Pintossi

"""
import sys
sys.path.append('..\\..')
import serial
import time
import asyncio
from List_connected_devices import find_port
from Logging_organizer.Logging_Setting import setup_logger


class SwitchValveArduino:
    def __init__(self, port, log_name, pins, valve_types):
        """Class to connect to an Arduino board running the sketch
        switch_pin_output.ino

        :param port: string
            Name of the serial port (e.g., 'COM4')
        :param log_name: string
            Name of the log file (e.g., 'Switching.log')
        :param pins: list
            List of digital pins to which the switch valves are connected
            (e.g., [8, 7, 4, 2])
        :param valve_types: list
            List of strings describing the type of valves (sorted in the same
            way as pins)
            (e.g., ['4-way', '3-way', '4-way', '3-way'])
        """
        self.port = port
        # Setup logging
        self.logger = setup_logger(f'{log_name}_logger', f'{log_name}.log')

        # Establish serial connection
        try:
            self.arduino = serial.Serial(
                port=port,
                baudrate=19200,
                timeout=.5,
            )
            self.logger.info(f"Connected to {len(pins)} valves")
        except serial.SerialException as error:
            self.logger.error(error)
            self.logger.info(f"Connection to valve FAILED")

        # Attribute storing the status of the digital output pins
        # 0 = LOW, 1= HIGH
        self.status = {i: j for i, j in zip(range(14), [0] * 14)}
        self.valve_types = valve_types
        self.digital_pins = pins
        self.valve_delay = .5  # time to let the valve move

        # Reset pins 2-13 to LOW
        for i in range(2, 14):
            self.set_to_status(i, 0)

    def find_valve_type(self, pin):
        """Method to identify the valve type given its digital pin.

        :param pin: int
            Digital pin to which the switch valve is connected
        :return:
            Switch valve type ('4-way' or '3-way')
        :rtype: string
        """
        return self.valve_types[self.digital_pins.index(pin)]

    def switch_valve(self, pin):
        """Method to change the position of the switch valve.
        0 --> 1
        1 --> 0

        :param pin: int
            Digital pin to which the switch valve is connected
        """
        signal = str(int(pin)).encode(encoding='ascii') + b'\n'
        while True:
            # Send signal to switch pin on/off
            self.arduino.write(signal)
            # Check execution
            feedback = self.arduino.readline().decode(encoding='ascii')
            if feedback != '':
                break
            time.sleep(.1)
        # Update status
        self.status[pin] = 0 if feedback == "LOW\n" else 1
        # Log status
        if self.status[pin] == 0:
            pos = 'C-1 (2-3)' if self.find_valve_type(pin) == '4-way' else 'ON'
        else:
            pos = 'C-3 (1-2)' if self.find_valve_type(pin) == '4-way' else 'OFF'
        self.logger.info(f'Valve on pin {pin} switched to {pos}.')

    def set_to_status(self, pin, status):
        """Set the switch valve to the desired status.

        :param pin: int
            Digital pin to which the switch valve is connected
        :param status: int
            Status of the desired output at the digital pin (0 = LOW, 1 = HIGH)
        """
        while True:
            if self.status[pin] == status:
                break
            else:
                self.switch_valve(pin)

    async def set_ON_or_C_1(self, pin):
        """Set the switch valve to ON or C-1.

        :param pin: int
            Digital pin to which the switch valve is connected
        """
        self.set_to_status(pin, 0)  # counterintuitive, based on valve behavior
        await asyncio.sleep(self.valve_delay)

    async def set_OFF_or_C_3(self, pin):
        """Set the switch valve to OFF or C-3.

        :param pin: int
            Digital pin to which the switch valve is connected
        """
        self.set_to_status(pin, 1)  # counterintuitive, based on valve behavior
        await asyncio.sleep(self.valve_delay)

    async def valve_1_ON_or_C_1(self):
        """Set valve 1 to ON or C-1.
        """
        if len(self.digital_pins) >= 1:
            await self.set_ON_or_C_1(self.digital_pins[0])

    async def valve_1_OFF_or_C_3(self):
        """Set valve 1 to OFF or C-3.
        """
        if len(self.digital_pins) >= 1:
            await self.set_OFF_or_C_3(self.digital_pins[0])

    async def valve_2_ON_or_C_1(self):
        """Set valve 2 to ON or C-1.
        """
        if len(self.digital_pins) >= 2:
            await self.set_ON_or_C_1(self.digital_pins[1])

    async def valve_2_OFF_or_C_3(self):
        """Set valve 2 to OFF or C-3.
        """
        if len(self.digital_pins) >= 2:
            await self.set_OFF_or_C_3(self.digital_pins[1])

    async def valve_3_ON_or_C_1(self):
        """Set valve 3 to ON or C-1.
        """
        if len(self.digital_pins) >= 3:
            await self.set_ON_or_C_1(self.digital_pins[2])

    async def valve_3_OFF_or_C_3(self):
        """Set valve 3 to OFF or C-3.
        """
        if len(self.digital_pins) >= 3:
            await self.set_OFF_or_C_3(self.digital_pins[2])

    async def valve_4_ON_or_C_1(self):
        """Set valve 4 to ON or C-1.
        """
        if len(self.digital_pins) >= 4:
            await self.set_ON_or_C_1(self.digital_pins[3])

    async def valve_4_OFF_or_C_3(self):
        """Set valve 4 to OFF or C-3.
        """
        if len(self.digital_pins) >= 4:
            await self.set_OFF_or_C_3(self.digital_pins[3])

    def close(self):
        self.arduino.close()


if __name__ == '__main__':
    myBoard = SwitchValveArduino(
        port=find_port('Switch_valves'),
        log_name='random_log_to_be_deleted.log',
        pins=[8, 7, 4, 2],
        valve_types=['3-way', '4-way', '3-way', '4-way'],
    )
    # asyncio.run(myBoard.valve_3_OFF_or_C_3())
    asyncio.run(myBoard.valve_4_ON_or_C_1())
    time.sleep(.5)
    asyncio.run(myBoard.valve_4_OFF_or_C_3())
    time.sleep(.5)
    asyncio.run(myBoard.valve_4_ON_or_C_1())
    time.sleep(.5)
    asyncio.run(myBoard.valve_4_OFF_or_C_3())
    # myBoard.switch_valve(8)
    # time.sleep(.5)
