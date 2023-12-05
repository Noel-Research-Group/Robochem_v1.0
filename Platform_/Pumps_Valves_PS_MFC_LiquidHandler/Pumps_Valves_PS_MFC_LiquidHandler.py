"""
Diego Pintossi, Zhenghui Wen, Aidan Slattery
Noël Research Group
Van 't Hoff Institute for Molecular Sciences (HIMS)
Universiteit van Amsterdam (UvA)

2021-07-27

Class to control
- syringe pumps,
- switch valves,
- MFC,
- phase sensors,
- liquid handler (requires Gsioc32.dll file from Gilson)
to prepare the gas bubbles (N2), wash volumes (pure solvent) and
reaction samples.

"""

import asyncio
import logging
import serial
import json
from Pumps_valves_MFC_PS_control.Pumps_valves_MFC_PS_control_v2 import PumpsValvesMFCPS
from Liquid_Handler.GX_241_Liquid_Handler import LiquidHandler
from Residence_time_control.Residence_time import find_flow_rate
from platform_class import Platform
from List_connected_devices import find_port



# CONSTANTS
SETUP_INFO_JSON = '../experimental_setup.json'
with open(SETUP_INFO_JSON) as json_file:
    experimental_setup = json.load(json_file)

SAMPlE_PUSH_VOLUME = experimental_setup["sample_push_volume"]


class SamplePreparation:
    def __init__(self, platform):
        """ Class initialization, setting up connections to instruments
        and logging.

        :param platform: (Platform_ class instance)
            Instance of the Platform_ class defined in platform_class.py
        """
        self.logger = logging.getLogger('Sample_preparation')
        logging.basicConfig(
            filename='Sample_presentation.log',
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%y-%m-%d %H:%M:%S',
            level=logging.INFO
        )
        try:
            self.liquid_handler = LiquidHandler()
            self.logger.info('Connected to Liquid Handler')
        except serial.SerialException as error:
            self.logger.warning(error)
            self.logger.info('Connection to Liquid Handler ensemble FAILED')

        try:
            self.pumps_valves = PumpsValvesMFCPS(platform)
            self.logger.info('Connected to Pumps+valves+MFC+PS')
        except serial.SerialException as error:
            self.logger.warning(error)
            self.logger.info(
                'Connection to Pumps+valves+MFC+PS ensemble FAILED'
            )
        self.switch_valves = platform.switch_valves

    async def system_start_up(self):
        """System initialization before sample injection.

        """
        # InjMod to INJECT
        await self.liquid_handler.switch_valve_position('VI')
        await asyncio.sleep(10)
        # fill everything with liquid till PS2
        # pump 1500 ml not needed
        # await self.pumps_valves.pump_liquid(
        #     volume=1500,  # μL
        #     flow_rate=1.5,  # mL/min
        #     phase_sensor='PS3',
        #     detect_sample=False,
        #     sensor_stop=False,
        #     continuous=False,
        #     bubbles=False
        # )

    async def slug_in_sample_loop(self, sample):
        """Sample preparation with liquid handler and injection in the sample
        loop in between nitrogen bubbles

        :param sample: tuple
            Tuple containing the list of all liquids to be mixed for the
            reaction sample.
        """
        # N2 till PS1
        # TODO check if we can rely on PS1 (wait_for_bubble=True)
        await self.pumps_valves.nitrogen_bubble(
            wait_time=25,
            wait_for_phase=True,
        )
        # InjMod to LOAD
        await self.liquid_handler.switch_valve_position('VL')
        # needle prepares sample and injects it
        await self.liquid_handler.prepare_reaction_sample(sample)
        # InjMod to INJECT
        await self.liquid_handler.switch_valve_position('VI')

    async def slug_out_to_reactor(self):
        """Pump the reaction slug out of the reactor, past PS2
            (slower to facilitate detection at PS3)
        """
        # push the slug out of the sample loop
        await self.pumps_valves.pump_liquid(
            volume=600,  # μL
            flow_rate=1,  # mL/min
            phase_sensor='PS3',
            detect_sample=True,
            sensor_stop=False,
            continuous=False,
            bubbles=False
        )
        # InjMod to LOAD
        await self.liquid_handler.switch_valve_position('VL')

    async def clean_sample_loop(self):
        """Cleaning of the needle and sample loop
        """
        # clean with Verity syringe pump (goes to waste via sample loop)
        await self.liquid_handler.clean_needle()

    async def slug_delivery(self, residence_time, reactor_volume):
        """Delivery of the reaction slug through the photoreactor and to the
        flow NMR at the desired flow rate.

        :param residence_time: float
            Desired residence time [s] for the reaction
        :param reactor_volume: float
            Internal volume of the flow reactor [mL]
        """
        print('in slug delivery')
        # deliver the sample to the reactor with desired flow rate (res time)
        await self.switch_valves.valve_4_ON_or_C_1()
        ### For UFO Flow Reactor ###
        # await self.pumps_valves.pump_liquid(
        #     3730,  # μL
        #     find_flow_rate(residence_time, reactor_volume),  # mL/min
        # )


        ### For Eagle ###
        await self.pumps_valves.pump_liquid(
            SAMPlE_PUSH_VOLUME,  # μL
            find_flow_rate(residence_time, reactor_volume),  # mL/min
        )

    async def full_sample_sequence(self,
                                   sample,
                                   residence_time,
                                   reactor_volume):
        print('Sample delivery - starting')
        await self.system_start_up()
        print('Sample delivery - preparing sample')
        await self.slug_in_sample_loop(sample)
        print('Sample delivery - ejecting sample')
        await self.slug_out_to_reactor()
        print('Sample delivery - delivery to reactor')
        await asyncio.gather(
            self.clean_sample_loop(),
            self.slug_delivery(residence_time, reactor_volume)
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
    S = SamplePreparation(platform)
    asyncio.run(S.slug_delivery(30, 4.0))
