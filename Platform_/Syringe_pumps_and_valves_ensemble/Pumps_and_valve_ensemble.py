"""
Diego Pintossi, Zhenghui Wen
Noël Research Group
Van 't Hoff Institute for Molecular Sciences (HIMS)
Universiteit van Amsterdam (UvA)

2021-09-13

Class to control two syringe pumps and a 4-way switch valve to enable
continuous operation.

Hardware:
- Arduino UNO
- Motorized 4-way switch valve (Runze fluid Mrv 01B-T03-K1.5-S-M04)
- 24V power source (Mean Well LRS-35-24)
- 12V power source
- 5V DC relay modules
- Syringe pumps (Chemyx Fusion 100 or 720)

                 bottle [2]
                  |
                  |
     |-[-|  ]=---(x)---=[  |-]-|
       pump_a     |     pump_b
          [1]     |        [3]
                 ...
                 [C]

switch valve C-1 (2-3): pump_a to setup, pump_b to reservoir
switch valve C-3 (1-2): pump_a to reservoir, pump_b to setup
place syringe pumps vertically to facilitate removal of bubbles

"""

import asyncio
import logging
from platform_class import Platform
from List_connected_devices import find_port


class PumpsValvesEnsemble:
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

        self.pump_A = platform.syringe_pump_a
        self.volume_A = 0
        self.pump_B = platform.syringe_pump_b
        self.volume_B = 0
        self.valves = platform.switch_valves

        self.active_pump = ''
        self.refill_vol = 9000
        self.refill_flow = 2
        self.logger.info('Pump+valves ensemble initialized')

    async def set_pump_active(self, active_pump):
        """ Coroutine to set one of the two syringe pumps as active,
        while the other is set to the refill position.

        :param active_pump: string
            'pump_a' to set Pump A as active and Pump B to refill
            'pump_b' to set Pump B as active and Pump A to refill
        """
        self.active_pump = active_pump
        await asyncio.sleep(1.5)  # to give enough time for refilling to start
        if active_pump == 'pump_a':
            await self.valves.valve_2_OFF_or_C_3()
            # Prime pump A
            await self.pump_A.operate_pump(650, 2)
            self.logger.info('Pump A set as active, Pump B set to refill')
        else:  # catches 'pump_b' and wrong input as well
            await self.valves.valve_2_ON_or_C_1()
            # Prime pump B
            await self.pump_B.operate_pump(650, 2)
            self.logger.info('Pump B set as active, Pump A set to refill')


    async def ensemble_start_up(self, fill_vol_a, fill_vol_b,
                                diameter_a=14.57, diameter_b=14.57):
        """ Coroutine to start-up the pumps-valves assembly.
        Multiple fill-empty-fill cycles to get rid of the bubbles.

        :param diameter_a: float
            internal diameter of syringe A [mm]
            defaults at 14.57 for 10 mL gas-tight syringes
        :param diameter_b: float
            internal diameter of syringe B [mm]
        :param fill_vol_a: float
            liquid volume to be filled in syringe A [μl]
        :param fill_vol_b: float
            liquid volume to be filled in syringe B [μl]
        """
        # [!] filling up cannot be at the same time now
        # [!] the 3-way valve will have to be positioned to the liquid side

        # set pumps parameters
        await asyncio.gather(
            asyncio.to_thread(self.pump_A.set_diameter, diameter_a),
            asyncio.to_thread(self.pump_B.set_diameter, diameter_b)
        )
        await asyncio.sleep(0.1)
        await asyncio.gather(
            asyncio.to_thread(self.pump_A.set_units, 'μL/min'),
            asyncio.to_thread(self.pump_B.set_units, 'μL/min')
        )
        await asyncio.sleep(0.1)

        # open way to waste
        await self.valves.valve_1_ON_or_C_1()

        # refill pump A / idle pump B
        await self.valves.valve_2_ON_or_C_1()
        await self.pump_A.operate_pump(-0.6 * fill_vol_a, 2)
        # empty pump A / refill pump B
        await self.valves.valve_2_OFF_or_C_3()
        await asyncio.gather(
            self.pump_A.operate_pump(0.4 * fill_vol_a, 2),
            self.pump_B.operate_pump(-0.6 * fill_vol_a, 2)
        )
        # fill pump A / empty pump B
        await self.valves.valve_2_ON_or_C_1()
        await asyncio.gather(
            self.pump_A.operate_pump(-0.4 * fill_vol_a, 2),
            self.pump_B.operate_pump(0.4 * fill_vol_a, 2)
        )
        # empty pump A / refill pump B
        await self.valves.valve_2_OFF_or_C_3()
        await asyncio.gather(
            self.pump_A.operate_pump(0.4 * fill_vol_a, 2),
            self.pump_B.operate_pump(-0.4 * fill_vol_a, 2)
        )
        # fill pump A / empty pump B
        await self.valves.valve_2_ON_or_C_1()
        await asyncio.gather(
            self.pump_A.operate_pump(-0.8 * fill_vol_a, 2),
            self.pump_B.operate_pump(0.4 * fill_vol_a, 2)
        )
        # idle pump A / refill pump B
        await self.valves.valve_2_OFF_or_C_3()
        await self.pump_B.operate_pump(-0.8 * fill_vol_a, 2)

        # store volumes
        self.volume_A = fill_vol_a
        self.volume_B = fill_vol_b
        self.logger.info(
            f"Syringe A and B filled with {(fill_vol_a + fill_vol_b) / 1000} "
            + "mL (in total)"
        )

        await self.set_pump_active('pump_a')

    async def ensemble_start_up_no_fill(self, diameter_a=14.57,
                                        diameter_b=14.57,
                                        vol_start_a=9000,
                                        vol_start_b=9000):
        """ Coroutine to start-up the pumps-valves assembly.
        Without fill-empty-fill cycles. Just setting valves to position
        and activating one pump.

        :param diameter_a: float
            internal diameter of syringe A [mm]
            defaults at 14.57 for 10 mL gas-tight syringes
        :param diameter_b: float
            internal diameter of syringe B [mm]
        :param vol_start_a: float
            liquid volume in syringe A [μl]
        :param vol_start_b: float
            liquid volume in syringe B [μl]
        """

        # set pumps parameters
        await asyncio.gather(
            asyncio.to_thread(self.pump_A.set_diameter, diameter_a),
            asyncio.to_thread(self.pump_B.set_diameter, diameter_b)
        )
        await asyncio.sleep(.1)
        await asyncio.gather(
            asyncio.to_thread(self.pump_A.set_units, 'μL/min'),
            asyncio.to_thread(self.pump_B.set_units, 'μL/min')
        )

        # open way to waste (3-way valve, 3A)
        await self.valves.valve_1_ON_or_C_1()

        # check which pump has more solvent and set it as the active pump
        await asyncio.sleep(.1)
        # syringes almost full --> no fill
        if vol_start_a > 8900 and vol_start_b > 8900:
            self.volume_A = vol_start_a
            self.volume_B = vol_start_b
            await self.set_pump_active('pump_a')
            self.logger.info(
                (
                        'Syringe A and B filled with '
                        + f'{(vol_start_a + vol_start_b) / 1000} mL (in total)'
                )
            )
        # syringes almost empty --> fill both
        elif vol_start_a < 2500 and vol_start_b < 2500:
            vol_for_refill1 = vol_start_a - self.refill_vol
            tasks1 = [
                asyncio.create_task(
                    self.pump_A.operate_pump(
                        vol_for_refill1, self.refill_flow
                    )
                ),
            ]
            await asyncio.wait(tasks1, return_when=asyncio.FIRST_COMPLETED)
            vol_for_refill2 = vol_start_b - self.refill_vol
            tasks2 = [
                asyncio.create_task(
                    self.set_pump_active('pump_a')
                ),
                asyncio.create_task(
                    self.pump_B.operate_pump(
                        vol_for_refill2, self.refill_flow
                    )
                ),
            ]
            await asyncio.wait(tasks2, return_when=asyncio.FIRST_COMPLETED)
            self.volume_A = self.refill_vol
            self.volume_B = self.refill_vol
            await self.set_pump_active('pump_a')
            self.logger.info(
                (
                        'Syringe A and B filled with '
                        + f'{(vol_start_a + vol_start_b) / 1000} mL (in total)'
                )
            )
        elif vol_start_a >= vol_start_b:
            vol_for_refill = vol_start_b - self.refill_vol
            tasks_a = [
                asyncio.create_task(
                    self.set_pump_active('pump_a')
                ),
                asyncio.create_task(
                    self.pump_B.operate_pump(
                        vol_for_refill, self.refill_flow
                    )
                ),
            ]
            await asyncio.wait(tasks_a, return_when=asyncio.FIRST_COMPLETED)
            self.volume_A = vol_start_a
            self.volume_B = self.refill_vol
            self.logger.info(
                (
                    'Syringe A and B filled with '
                    + f'{(vol_start_a + self.refill_vol) / 1000} mL (in total)'
                )
            )
        elif vol_start_a < vol_start_b:
            vol_for_refill = vol_start_a - self.refill_vol
            tasks_b = [
                asyncio.create_task(
                    self.set_pump_active('pump_b')
                ),
                asyncio.create_task(
                    self.pump_A.operate_pump(
                        vol_for_refill, self.refill_flow
                    )
                ),
            ]
            await asyncio.wait(tasks_b, return_when=asyncio.FIRST_COMPLETED)
            self.volume_A = self.refill_vol
            self.volume_B = vol_start_b
            self.logger.info(
                (
                    'Syringe A and B filled with '
                    + f'{(self.refill_vol + vol_start_b) / 1000} mL (in total)'
                )
            )

    async def operate_ensemble(self, volume, flow_rate):
        """ Coroutine to operate the ensemble of pumps and switch valves.
        Manages the active pump and refilling based on required volume.

        :param volume: float
            Volume [μL] to be dispensed
        :param flow_rate: float
            Flow rate [mL/min] to be used for dispensing
        """
        if volume <= 0 or volume >= 10000:
            self.logger.warning('Invalid volume (volume <= 0 or >= 10000).')
        elif self.active_pump == 'pump_a':
            if self.volume_A > volume:
                await self.pump_A.operate_pump(volume, flow_rate)
                self.volume_A -= volume
                self.logger.info(f"Pump A dispensed {volume} μL")
            else:
                self.active_pump = 'pump_b'
                self.logger.info('Switching pumps. Refilling and dispensing.')
                await self.set_pump_active(self.active_pump)
                refill_vol = - (self.refill_vol - self.volume_A)
                self.volume_A = self.refill_vol
                self.volume_B -= volume
                tasks = [
                    asyncio.create_task(
                        self.pump_A.operate_pump(refill_vol, self.refill_flow)
                    ),
                    asyncio.create_task(
                        self.pump_B.operate_pump(volume, flow_rate)
                    )
                ]
                await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        elif self.active_pump == 'pump_b':
            if self.volume_B > volume:
                await self.pump_B.operate_pump(volume, flow_rate)
                self.volume_B -= volume
                self.logger.info(f'Pump B dispensed {volume} μL')
            else:
                self.active_pump = 'pump_a'
                self.logger.info('Switching pumps. Refilling and dispensing.')
                await self.set_pump_active(self.active_pump)
                refill_vol = - (self.refill_vol - self.volume_B)
                self.volume_B = self.refill_vol
                self.volume_A -= volume
                tasks = [
                    asyncio.create_task(
                        self.pump_B.operate_pump(refill_vol, self.refill_flow)
                    ),
                    asyncio.create_task(
                        self.pump_A.operate_pump(volume, flow_rate)
                    )
                ]
                await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

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

    pumps_valves = PumpsValvesEnsemble(platform)
    asyncio.run(pumps_valves.operate_ensemble(5000, 1.5))


