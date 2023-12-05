"""
Diego Pintossi, Zhenghui Wen
Noël Research Group
Van 't Hoff Institute for Molecular Sciences (HIMS)
Universiteit van Amsterdam (UvA)

2021-07-01

Class to control the mass flow controller.
Based on the Bronkhorst-Propar library available from PyPi.
(pip install bronkhorst-propar)

Hardware:
- Bronkhorst MFC

"""

import propar
import asyncio
import serial
from List_connected_devices import find_port
from Logging_organizer.Logging_Setting import setup_logger


class BronkhorstMFC:
    def __init__(self, port):
        """ Class initialization connecting to the Mass Flow Controller (MFC)

        :param port: (string)
            Serial port name connected to the MFC
        """
        # self.port = port
        self.logger = setup_logger('MFC_logger', 'MFC_logger.log')
        try:
            self.instrument = propar.master(port, baudrate=38400)
        except serial.SerialException as error:
            self.logger.warning(error)
            self.logger.error(f"Connection to MFC failed.")

        self.logger.info(f"MFC connected on port {port}.")
        self.min_flow = 0.014
        # self.max_flow = 25  # 25 mln/min O2 7bar/1bar
        # self.max_flow = 1   # 1 mln/min N2 7bar/1bar
        self.max_flow = 1   # 1 mln/min O2 7bar/3bar

    def calculate_setpoint(self, flow):
        """ Function to calculate a gas flow in [mln/min] to a setpoint
        in the 0...32000 range.

        :param flow: (float)
            Desired gas flow rate [mln/min]
        :return: (float)
            Setpoint in the 0...32000 range for the MFC
        """
        instr_range = self.max_flow - self.min_flow
        return int(32000 * (flow - self.min_flow) / instr_range)

    def convert_reading(self, measured):
        """ Function to convert the reading from the instrument
        from 0...32000 range to [mln/min]

        :param measured: (float)
            Measured gas flow rate in the 0...32000 range
        :return: (float)
            Measured gas flow rate [mln/min]
        """
        instr_range = self.max_flow - self.min_flow
        return self.min_flow + measured * instr_range / 32000

    async def define_setpoint(self, flow):
        """ Coroutine to establish the setpoint for the MFC.
        The input is normal milliliters per minute [mln/min].
        setpoint = 0 --> min flow rate
        setpoint = 32000 --> max flow rate
        Default min/max flow rates are defined for our instrument
        (Bronkhorst EL-FLOW F-200CV-002-RAD-22-V) and gas (N2).

        :param flow: (float)
            Desired flow rate [mln/min]
        """
        await asyncio.sleep(0.1)
        if flow < self.min_flow or flow > self.max_flow:
            self.logger.warning(f"Invalid input flow rate: {flow} mln/min")
            if flow < self.min_flow:
                self.logger.info(
                    f"Flow rate too low. Set MFC flow rate: {self.min_flow} mln/min"
                )
                await asyncio.sleep(0.1)
                self.instrument.setpoint = 0  # min value
                self.logger.info(f"Set MFC flow rate: {self.min_flow} mln/min")
            elif flow > self.max_flow:
                self.logger.info(
                    f"Flow rate too high. Set MFC flow rate: {self.max_flow} mln/min"
                )
                await asyncio.sleep(0.1)
                self.instrument.setpoint = 32000  # max value
                self.logger.info(f"Set MFC flow rate: {self.max_flow} mln/min")
        else:
            await asyncio.sleep(0.1)
            self.instrument.setpoint = self.calculate_setpoint(flow)
            self.logger.info(f"Set MFC flow rate: {flow} mln/min")

    async def read_flow(self):
        """ Coroutine to read the current flow rate through the MFC.

        :return: (float)
            Gas flow rate [mln/min]
        """
        gas_flow = self.instrument.measure
        await asyncio.sleep(0.1)
        converted = self.convert_reading(gas_flow)
        self.logger.info(f"Flow rate reading from MFC: {converted} mln/min")
        return converted

    def close(self):
        self.instrument.stop()


if __name__ == "__main__":
    mfc = BronkhorstMFC(find_port('MFC'))
    flow_test = 200 # 0.014
    print(mfc.calculate_setpoint(flow_test))
    asyncio.run(mfc.define_setpoint(flow_test))
