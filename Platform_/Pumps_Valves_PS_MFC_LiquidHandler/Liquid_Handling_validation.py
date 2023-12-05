# -*- coding: utf-8 -*-

""" Script to validate the liquid handling part of the platform

Diego Pintossi
Noël Research Group
Van 't Hoff Institute for Molecular Sciences (HIMS)
Universiteit van Amsterdam (UvA)

2021-10-25

Validation of the sample injection sequence.
Including:
    - sample detection from phase sensors
    - LH control
    - pumps & valves
"""

import asyncio
import time
from platform_class import Platform
from List_connected_devices import find_port
from Pumps_Valves_PS_MFC_LiquidHandler.Pumps_Valves_PS_MFC_LiquidHandler import SamplePreparation  # same folder

if __name__ == "__main__":
    # 1. connect
    myPlatform = Platform(
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
        # syringe_pump_c={
        #     'port': find_port('Syringe_pump_C'),
        #     'baudrate': 38400,
        #     'name': 'syringe_pump_c'
        # },
        switch_valves={
            'port': find_port('Switch_valves'),
            'pins': [8, 7, 4, 2],
            'name': 'switch_valves',
            'valve types': [
                '3-way', '4-way', '3-way', '4-way'
            ]
        },
        mfc={'port': find_port('MFC')},
        phase_sensors_a={
            'port': find_port('Phase_sensors_A'),
            'pins': [0, 1, 2],
            'name': 'phase_sensors_a'
        }  # ,
        # phase_sensors_b={
        #     'port': find_port('Phase_sensors_B'),
        #     'pins': [0, 1, 2, 3],
        #     'name': 'phase_sensors_b'
        # }
    )

    # 2. Fill-up pumps
    liquid_handling = SamplePreparation(myPlatform)
    full_start_up = False  # True if syringes need to be filled
    if full_start_up:
        # first time
        asyncio.run(
            liquid_handling.pumps_valves.PumpsValvesEnsemble.ensemble_start_up(
                fill_vol_a=8000,  # volumes MUST be in microliters!
                fill_vol_b=8000,
                diameter_a=14.47,  # SGE syringe (gas-tight)
                diameter_b=14.47
            )
        )
    else:
        # after first time (adjust volumes!)
        asyncio.run(
            liquid_handling.pumps_valves.PumpsValvesEnsemble.ensemble_start_up_no_fill(
                vol_start_a=4000,  # volumes MUST be in microliters!
                vol_start_b=6500,
                diameter_a=14.47,
                diameter_b=14.47
            )
        )

    # 3. Verify INJECT/LOAD positions
    GX_241 = liquid_handling.liquid_handler  # for simplicity
    asyncio.run(
        GX_241.home()  # home the liquid handler modules
    )
    print('LH is homed.')
    step_3_test = False
    if step_3_test:
        # 3.1 INJECT
        inject = False
        if inject:
            asyncio.run(
                GX_241.switch_valve_position('VI')
            )
            print('Injection Module @ INJECT')
            time.sleep(1)
            asyncio.run(GX_241.move_Z(122))
            time.sleep(1)
            asyncio.run(GX_241.move_XY(146.05, 0))
            time.sleep(1)
            asyncio.run(GX_241.move_Z(93.1))
            time.sleep(1)
            print('Start cleaning.')
            asyncio.run(GX_241.clean_needle())
            print('Stop cleaning.')
            time.sleep(1)
        # 3.2 LOAD
        load = True
        if load:
            asyncio.run(
                GX_241.switch_valve_position('VL')
            )
            print('Injection Module @ LOAD')
            time.sleep(1)
            asyncio.run(GX_241.move_Z(122))
            time.sleep(1)
            asyncio.run(GX_241.move_XY(146.05, 0))
            time.sleep(1)
            asyncio.run(GX_241.move_Z(93.1))
            time.sleep(1)
            print('Start cleaning.')
            asyncio.run(GX_241.clean_needle())
            print('Stop cleaning.')
            time.sleep(1)

    # 4. Check data export from phase sensors
    data_export_test = False


    async def test_export():
        try:
            await asyncio.wait_for(
                myPlatform.phase_sensors_start_export(),
                timeout=10
            )
        except asyncio.TimeoutError:
            print('Export loop timed out.')


    if data_export_test:
        print(time.time())
        asyncio.run(
            test_export()
        )
        print(time.time())

    # 5. Test droplet detection sequence
    droplet_detect = True
    syringe_pumps = liquid_handling.pumps_valves.PumpsValvesEnsemble
    if droplet_detect:
        # 5.1 injection module to LOAD position
        asyncio.run(
            GX_241.switch_valve_position('VL')
        )
        # 5.2 fill everything with solvent till PS3
        vol_to_fill = 800
        asyncio.run(
            syringe_pumps.operate_ensemble(
                vol_to_fill,
                2.0
            )
        )
        print('Tubing should be full of solvent.')


        # 5.3 export loop and droplets + detection
        async def create_bubble_droplet_bubble():
            for _ in range(5):
                # bubble
                await liquid_handling.pumps_valves.prepare_slug(
                    200,
                    1,
                    pin=0
                )
                # droplet-bubble
                await liquid_handling.pumps_valves.prepare_slug(
                    450,
                    1,
                    pin=0
                )
                # move forward
                await syringe_pumps.operate_ensemble(
                    1500,
                    1
                )


        async def delayed_detect():  # OUTDATED!!!
            await asyncio.sleep(90)
            await myPlatform.phase_sensor_2.droplet_detection_loop(
                analysed_interval=180,
                frequency=1
            )


        async def detection_test():
            detection_tasks = [
                asyncio.create_task(
                    create_bubble_droplet_bubble()
                ),
                asyncio.create_task(
                    myPlatform.phase_sensors_start_export()
                ),
                asyncio.create_task(
                    delayed_detect()
                )
            ]
            await asyncio.wait(
                detection_tasks,
                return_when=asyncio.FIRST_COMPLETED
            )


        asyncio.run(
            detection_test()
        )

    # 6. Test the sample delivery sequence
    sample_delivery_seq = False
    if sample_delivery_seq:
        async def sample_prep_test():
            sample_tasks = [
                asyncio.create_task(
                    liquid_handling.full_sample_sequence(
                        [['338S', 1, 1, 400]],  # sample
                        120,  # 2 min residence time
                        2  # 2 mL reactor
                    )
                ),
                asyncio.create_task(
                    myPlatform.phase_sensors_start_export()
                )
            ]
            await asyncio.wait(
                sample_tasks,
                return_when=asyncio.FIRST_COMPLETED
            )


        asyncio.run(
            sample_prep_test()
        )
        # TO BE COMPLETED
