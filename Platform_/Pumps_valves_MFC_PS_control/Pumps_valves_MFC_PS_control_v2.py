"""
Diego Pintossi, Zhenghui Wen, Aidan Slattery
Noël Research Group
Van 't Hoff Institute for Molecular Sciences (HIMS)
Universiteit van Amsterdam (UvA)

2021-09-14

Class to control two syringe pumps, four switch valves and a MFC
to prepare the gas (N2) and liquid (pure solvent) carrier volumes.

Hardware:
- Arduino UNO
- Motorized switch valves (Runze fluid Mrv 01B-T03-K1.5-S-M02)
- 24V power source (Mean Well LRS-150-24)
- 12V power source
- 5V DC relay modules
- Syringe pumps (Chemyx Fusion 100 / 720, not 200)
- Bronkhorst MFC
- TT electronics OCB350 phase sensor (PS)

                 bottle
                  |
                  |
     |-[-|  ]=---(x)---=[  |-]-|
       pump_a     |     pump_b
                  |
                 ( )--[PS]--->
                  |
                [MFC]
                  |


4-way switch valve:
    C-1 (2-3) = pump_a to setup, pump_b to reservoir
    C-3 (1-2) = pump_a to reservoir, pump_b to setup

3-way switch valve:
    ON  = to syringe pumps,
    OFF = to MFC

[!] place syringe pumps a and b vertically to facilitate removal of bubbles
[!] place phase sensor as close as possible to outlet of 3-way switch valve

"""

import logging

import pandas as pd

import phase_sensor_CSV_naming
from Phase_sensors.Phase_sensor_detection import *
from Syringe_pumps_and_valves_ensemble.Pumps_and_valve_ensemble import PumpsValvesEnsemble
from platform_class import Platform
from List_connected_devices import find_port


# This Class has been changed to read from csv instead of phase sensor
class PumpsValvesMFCPS:
    def __init__(self, platform):
        """ Class initialization setting up connection to the
        instruments and logging.

        :param platform: Platform_ class instance
            Instance of the Platform_ class defined in platform_class.py
        """
        self.logger = logging.getLogger('Pumps_Valves_MFC_PS')
        logging.basicConfig(
            filename='Pumps_Valves_MFC_PS.log',
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%y-%m-%d %H:%M:%S',
            level=logging.DEBUG,
        )

        self.platform = platform
        self.PumpsValvesEnsemble = PumpsValvesEnsemble(platform)
        self.MFC = platform.mfc

    # Need to import these from somewhere
    async def phase_is_gas(self, pin=0, board='phase_sensors_A'):
        """Function to check the phase detected by a phase sensor.

        :param pin: integer
            the analog pin number where the sensor is connected
        :param board: string
            the name of the board where the sensor is connected
        """
        filename = pd.read_csv(
            phase_sensor_CSV_naming.get_CSV_with_names_ps(),
            index_col=0
        )['0'][pin]
        ps_data = pd.read_csv(filename)
        last_data = ps_data['Phase'][len(ps_data)-1]
        if last_data == 0:
            return True
        else:
            return False

    # [!] unused
    async def prepare_slug(self, liquid_vol, liquid_flow_rate):
        # likely not going to be used in final version
        """ Method to prepare a liquid volume followed by a nitrogen one.

        :param liquid_vol: (float)
            Volume of liquid [μL] to be dispensed
        :param liquid_flow_rate: (float)
            Flow rate [mL/min] to be used for dispensing the liquid
        """
        # liquid volume
        await self.PumpsValvesEnsemble.valves.valve_1_ON_or_C_1()
        await asyncio.gather(
            self.PumpsValvesEnsemble.operate_ensemble(
                liquid_vol,
                liquid_flow_rate
            ),
            self.MFC.define_setpoint(self.MFC.min_flow)
        )

        # gas volume
        await self.PumpsValvesEnsemble.valves.valve_1_OFF_or_C_3()
        await self.MFC.define_setpoint(0.10)
        while await self.phase_is_gas():  # N2 flow until bubble comes out
            await asyncio.sleep(0.050)  # check every 100 ms
        await self.MFC.define_setpoint(self.MFC.min_flow)
        await self.PumpsValvesEnsemble.valves.valve_1_ON_or_C_1()

    async def nitrogen_bubble(self, wait_time=5,
                              wait_for_phase=True):
        """Injects a N2 volume using the MFC and the three-way switch valve.
        The built-in phase_is_gas() function checks PS1 by default.

        :param wait_time: float
            Wait time before the N2 flow is cut off
        :param wait_for_phase: bool
            Boolean deciding whether the nitrogen flow should be cut off based
            on signal from phase sensor (True) or based on a defined waiting
            time (False)
        """
        # valve to MFC
        await self.PumpsValvesEnsemble.valves.valve_1_OFF_or_C_3()
        # start flow N2
        await self.MFC.define_setpoint(1)  # N2 flow to min
        if wait_for_phase:
            while not await self.phase_is_gas():  # N2 flow until bubble reaches PS1
                # out
                await asyncio.sleep(0.100)  # check every 100 ms
        else:
            await asyncio.sleep(wait_time)
        # stop flow N2
        await self.MFC.define_setpoint(0)  # self.MFC.min_flow)
        # valve back to syringe pumps
        await self.PumpsValvesEnsemble.valves.valve_1_ON_or_C_1()

    async def pump_liquid(self, volume, flow_rate,
                          phase_sensor='PS1', detect_sample=False,
                          sensor_stop=False, continuous=False,
                          bubbles=False):
        """Method to (continuously) pump liquid at a desired flow rate.
        The built-in phase_is_gas() function checks PS1 by default.

        :param volume: float
            Volume of liquid [μL] delivered in every pumping cycle
        :param flow_rate: float
            Flow rate [mL/min] used to deliver the liquid
        :param phase_sensor: string
            Name of the phase sensor detecting the reaction slug passing.
        :param detect_sample: bool
            Whether the pumping loop should stop when the reaction slug
            passes a given phase sensor (identified by its data file) [only
            PS2 or PS3]
        :param sensor_stop: bool
            Whether the liquid delivery should be stopped based on the
            the signal from a phase sensor (PS1)
        :param continuous: bool
            Whether the pumping should be repeated in an infinite loop
        :param bubbles: bool
            Whether N2 bubbles should separate the liquid volumes
        :param bubbles
        """
        if sensor_stop:
            while await self.phase_is_gas():  # PS1 by default values
                await self.PumpsValvesEnsemble.operate_ensemble(
                    volume, flow_rate
                )
        elif detect_sample:
            while True:
                # pump set volume
                await self.PumpsValvesEnsemble.operate_ensemble(
                    volume, flow_rate
                )
                # wait to allow for signal processing
                await asyncio.sleep(2)
                # check for droplet
                detected = await identify_reaction_mix(
                    ps_data_filename(phase_sensor),
                    droplet_data_filename(phase_sensor),
                    sample_time=120,
                )
                # break loop if droplet detected
                if detected:
                    break
        elif continuous:
            # keep pumping the solvent
            while True:
                await self.PumpsValvesEnsemble.operate_ensemble(
                    volume, flow_rate
                )
                if bubbles:
                    await self.nitrogen_bubble()
        else:
            await self.PumpsValvesEnsemble.operate_ensemble(
                volume, flow_rate
            )

if __name__ == '__main__':
    platform = Platform(
        syringe_pump_a={
            'port': find_port('Syringe_pump_A'),
            'baudrate': 38400,
            'name': 'syringe_pump_a'
        },
        syringe_pump_b={
            'port': find_port('Syringe_pump_B'),
            'baudrate': 38400,
            'name': 'syringe_pump_b'
        },
        syringe_pump_c={
            'port': find_port('Syringe_pump_C'),
            'baudrate': 38400,
            'name': 'syringe_pump_c'
        },
        switch_valves={
            'port': find_port('Switch_valves'),
            'name': 'switch_valves',
            'pins': [8, 7, 4, 2],
            'valve types': ['3-way', '4-way', '3-way', '4-way']
        },
        mfc={'port': find_port('MFC')},
    )

    pumps_valves = PumpsValvesMFCPS(platform)
    asyncio.run(pumps_valves.nitrogen_bubble())




