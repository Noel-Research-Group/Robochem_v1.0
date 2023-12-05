"""
Diego Pintossi, Zhenghui Wen
Noël Research Group
Van 't Hoff Institute for Molecular Sciences (HIMS)
Universiteit van Amsterdam (UvA)

2022-01-12

Class to control a single syringe pumps and three switch valves to enable
continuous operation.

Hardware:
- Arduino UNO
- Motorized 3-way switch valve (Runze fluid Mrv 01B-T03-K1.5-S-M03)
- 24V power source (Mean Well LRS-35-24)
- 12V power source
- 5V DC relay modules
- Syringe pumps (Chemyx Fusion 100 or 720)

                 bottle [ON]
                  |
                  |
     |-[-|  ]=---(x)
       pump_c     |
          [C]     |
                 to NMR loop [OFF]

switch valve ON: pump_a to setup, pump_b to reservoir
switch valve OFF: pump_a to reservoir, pump_b to setup
place syringe pumps vertically to facilitate removal of bubbles

"""

import asyncio
import logging

# Dubugging
# from Pumps_valves_MFC_PS_control.Pumps_valves_MFC_PS_control_v2 import PumpsValvesMFCPS
from platform_class import Platform
from List_connected_devices import find_port
from Phase_sensors.Phase_sensor_detection import *

class SinglePumpValveEnsemble:
    def __init__(self, platform):
        """ Class initialization

        :param platform: Platform_ class instance
            Dictionary storing parameters to connect to pump A.
            {'port': port, 'baudrate': baudrate, 'name': name}
        """
        self.logger = logging.getLogger('Pump_ensemble_log')
        logging.basicConfig(
            filename='Automation_log.log',
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%y-%m-%d %H:%M:%S',
            level=logging.DEBUG
        )

        self.pump_C = platform.syringe_pump_c
        # self.volume_C = 0
        self.volume_C = 10000
        self.valve = platform.switch_valves

        self.refill_vol = 10000
        self.logger.info('Pump+valves ensemble initialized')
        # self.PumpsValvesMFCPS = PumpsValvesMFCPS(platform)

    async def pump_start_up(self, fill_vol_c, diameter_c=14.57):
        """ Coroutine to start-up the pumps-valves assembly.
        Multiple fill-empty-fill cycles to get rid of the bubbles.

        :param diameter_c: float
            internal diameter of syringe C [mm]
            defaults at 14.57 for 10 mL gas-tight syringes (SGE)
        :param fill_vol_c: float
            liquid volume to be filled in syringe C [μl]
        """
        # set pumps parameters
        await asyncio.to_thread(self.pump_C.set_diameter, diameter_c)
        await asyncio.sleep(0.1)
        await asyncio.to_thread(self.pump_C.set_units, 'μL/min')
        await asyncio.sleep(0.1)

        # open way to reservoir
        await self.valve.valve_3_ON_or_C_1()
        # refill pump C
        await self.pump_C.operate_pump(-0.6 * fill_vol_c, 2)
        # empty pump C
        await self.pump_C.operate_pump(0.4 * fill_vol_c, 2)
        # refill pump C
        await self.pump_C.operate_pump(-0.4 * fill_vol_c, 2)
        # empty pump C
        await self.pump_C.operate_pump(0.4 * fill_vol_c, 2)
        # refill pump C
        await self.pump_C.operate_pump(-0.8 * fill_vol_c, 2)
        # open way to NMR loop
        await self.valve.valve_3_OFF_or_C_3()

        # store volumes
        self.volume_C = fill_vol_c
        self.logger.info(
            f"Syringe C filled with {fill_vol_c / 1000} "
            + "mL (in total)"
        )

    async def pump_start_up_no_fill(self, diameter_c=23.03,
                                    vol_start_c=5000):
        """ Coroutine to start-up the pump-valve assembly.
        Without fill-empty-fill cycles. Just setting valves to position
        and activating one pump.

        :param diameter_c: float
            internal diameter of syringe C [mm]
            defaults at 14.57 for 10 mL gas-tight syringes
        :param vol_start_c: float
            liquid volume in syringe C [μl]
        """
        # set pumps parameters
        await asyncio.to_thread(self.pump_C.set_diameter, diameter_c)
        await asyncio.sleep(.250)
        await asyncio.to_thread(self.pump_C.set_units, 'μL/min')
        await asyncio.sleep(.250)

        # open way to NMR loop
        await self.valve.valve_3_OFF_or_C_3()

        # store volumes
        self.volume_C = vol_start_c
        self.logger.info(
            f"Syringe C starting with {vol_start_c / 1000} "
            + "mL (in total)"
        )

    async def refill_syringe(self):
        """Method to refill the syringe.
        """
        # open way to reservoir
        await self.valve.valve_3_ON_or_C_1()
        refill_vol = - (self.refill_vol - self.volume_C)
        if abs(refill_vol) > 500:  # only run pump if needed
            await self.pump_C.operate_pump(refill_vol, 3)
        self.volume_C = self.refill_vol
        self.logger.info('Refilled Syringe C.')
        # open way to reservoir
        await self.valve.valve_3_OFF_or_C_3()

    async def operate_ensemble(self, volume, flow_rate):
        """Coroutine to operate the ensemble of pumps and switch valves.
        Manages the active pump and refilling based on required volume.

        :param volume: float
            Volume [μL] to be dispensed
        :param flow_rate: float
            Flow rate [mL/min] to be used for dispensing
        """
        if volume <= 0 or volume >= 10000:
            self.logger.warning('Invalid volume (volume <= 0 or >= 10000).')
        else:
            if self.volume_C > volume:
                await self.pump_C.operate_pump(volume, flow_rate)
                self.volume_C -= volume
                self.logger.info(f"Pump C dispensed {volume} μL")
            else:
                await self.refill_syringe()

    # async def pump_to_analysis(self):
    #     """Pump the reaction slug to the reactor, past PS2
    #                 (slower to facilitate detection at PS3)
    #             """
    #     # push the slug out of the sample loop
    #     await pump_liquid_pump_c(
    #         volume=80,  # μL
    #         flow_rate=1,  # mL/min
    #         phase_sensor='PS4',
    #         detect_sample=True,
    #         continuous=False
    #     )

    async def pump_to_analysis(self, volume, flow_rate,
                          phase_sensor='PS4', detect_sample=True,
                          continuous=False):
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

        if detect_sample:
            while True:
                # pump set volume
                await self.pump_C.operate_pump(
                    volume, flow_rate
                )
                # wait to allow for signal processing
                await asyncio.sleep(2)
                # check for droplet
                detected = await identify_reaction_mix(
                    ps_data_filename(phase_sensor),
                    droplet_data_filename(phase_sensor),
                    sample_time=350,
                )
                # break loop if droplet detected
                if detected:
                    break
        elif continuous:
            # keep pumping the solvent
            while True:
                await self.pump_C.operate_pump(
                    volume, flow_rate
                )
        else:
            await self.pump_C.operate_pump(
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
    analysis_pump = SinglePumpValveEnsemble(platform)
    asyncio.run(analysis_pump.pump_C.Single_pump_and_valve_ensemble.pump_liquid_pump_c(
        volume=80,  # μL
        flow_rate=1,  # mL/min
        phase_sensor='PS4',
        detect_sample=True,
        continuous=False
    )
    )
