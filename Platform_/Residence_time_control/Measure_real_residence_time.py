"""
Diego Pintossi
Noël Research Group
Van 't Hoff Institute for Molecular Sciences (HIMS)
Universiteit van Amsterdam (UvA)

2021-10-20

Functions to analyze the signal from two phase sensors placed at the inlet
and outlet of the photoreactor to estimate the real residence time of the
reaction slug.
"""

import asyncio
from Phase_sensors.Phase_sensor_detection import droplet_detection_loop
import time


async def measure_time_of_detection(phase_sensor):
    """ Register the time at which the reaction droplet is detected by
    a phase sensor.

    :param phase_sensor: string
        The name of the phase sensor (e.g., 'PS1' for Phase Sensor 1).
    :return: float
        Time at which the analysis of phase sensor data reveals a reaction
        slug
    """
    t = time.time() if await droplet_detection_loop(
        phase_sensor,
        analysed_interval=90,
        frequency=1
    ) else 0
    return t


async def find_residence_time(target):
    """ Calculate the residence time of the reaction droplet between two
    phase sensors.

    :param target: float
        The desired residence time [s].
    :return: float, float
        [0] = the measured residence time
        [1] = the % deviation from the target residence time (class
        attribute)
    """
    t4, t5 = await asyncio.gather(
        measure_time_of_detection('PS4'),
        measure_time_of_detection('PS5')
    )
    residence_time = t5 - t4
    deviation = 100 * (residence_time - target) / target  # [%]
    return residence_time, deviation
