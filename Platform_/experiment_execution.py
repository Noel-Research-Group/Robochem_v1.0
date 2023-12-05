"""Functions to execute a single experiment with the automated platform

 Aidan Slattery, D.Pintossi

"""

import asyncio
from Phase_sensors.Phase_sensor_board import phase_sensor_1, phase_sensor_2, \
    phase_sensor_3, phase_sensor_4, phase_sensor_5, phase_sensor_6, \
    phase_sensor_7
from phase_sensor_CSV_naming import *
from NMR_control_loop.NMR_loop import NMRLoop
from phase_sensor_CSV_naming import get_your_abs_project_path
from Phase_sensors.Phase_sensor_detection import ps_data_filename
import pandas as pd
from platform_class import Platform
from List_connected_devices import find_port
from Liquid_Handler.Sample_info import SampleInfo


async def experimental_sequence(
        platform, liquid_handling, pump_C,
        chemical_space, sample, residence_time, reactor_volume
):
    """sub-routine to coordinate the liquid handler pumps and NMR to deliver, reac, and analyse the slug
    :param platform:
    :param liquid_handling:
    :param pump_C:
    :param sample:
    :param residence_time:
    :param reactor_volume:
    :return:
    """
    # 1. Cleaning or cycle start-up
    print('LH homing')
    await liquid_handling.liquid_handler.Gilson_identification()
    # 2. Sample preparation + delivery // NMR analysis

    nmr_loop = NMRLoop(platform, pump_C, residence_time, chemical_space)
    await liquid_handling.full_sample_sequence(
            sample,
            residence_time,
            reactor_volume
            )
    await nmr_loop.the_loop_TBADT()

async def single_automated_experiment(
        platform, liquid_handling, pump_C,
        chemical_space, sample, residence_time, reactor_volume
):
    """sub-routine to set up the sample for delivery, call experimental sequence
    to deliver the slug, read and return the yield reported by the NMR analysis
    of the slug
    """
    # Create the names for the CSV files where PS log data
    create_list_of_CSV_names()
    frequency = 1  # NOTE: there is a 500+ ms overhead (1 s --> ~1.6 s)

    # set up loop for initializing the phase sensors, execute the experiment,
    # & check for yield data
    experiment_successful = False
    while not experiment_successful:
        # Set-up tasks for PS data export
        # (new files for every experiment)
        ps1 = asyncio.create_task(
            phase_sensor_1(frequency)
        )
        ps2 = asyncio.create_task(
            phase_sensor_2(frequency)
        )
        ps3 = asyncio.create_task(
            phase_sensor_3(frequency)
        )

        # ps5 = asyncio.create_task(
        #     phase_sensor_5(frequency)
        # )
        # ps7 = asyncio.create_task(
        #     phase_sensor_7(frequency)
        # )

        # Set-up task for the execution of the experiment
        experiment = asyncio.create_task(
            experimental_sequence(
                platform, liquid_handling, pump_C,
                chemical_space, sample, residence_time, reactor_volume,
            )
        )

        tasks = [
            ps1, ps2, ps3,
            experiment,
        ]

        await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_COMPLETED
        )

        # read yield csv from NMR
        yield_csv = (get_your_abs_project_path()
                     + 'NMR_DATA'
                     + '\\NMR_DATA_PROCESSED'
                     + f'\\Processed_NMR_data'
                       f'_{ps_data_filename("PS1")[-24:-8]}.csv')

        df = pd.read_csv(yield_csv)
        experiment_successful = True

        await asyncio.sleep(5)

    # format and return measured yield
    measured_yield = float(df['Yield'])
    if 0.5 > measured_yield > -9:
        measured_yield = 0
    elif measured_yield < -10:
        measured_yield = 0
        # raise ValueError('Value is too low, possibly an error has occurred')
    print(f'single automated experiment yield: {measured_yield}')
    return measured_yield

