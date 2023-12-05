"""Script to test connection to multiple Arduino boards.

D.Pintossi
2022-01-15
"""

import random
import asyncio
from Phase_sensors.OPB350_IO_Arduino_sketch import PhaseSensor
from List_connected_devices import find_port
from Switch_valves.Switch_valve_multi import SwitchValveMulti


# Connect to the board with the switch valves via pyFirmata
pins = [8, 7, 4, 2]
types = ['4-way', '3-way','4-way', '3-way']
myValves = SwitchValveMulti(
    find_port('Switch_valves'),
    pins,
    'Switch_valves_log_123',
    types
)

# Connect to the boards with the phase sensors via pyserial (new class)
ps1 = PhaseSensor(
    find_port('PS1'),
    1,
    'Log_ps1.log'
)
ps2 = PhaseSensor(
    find_port('PS2'),
    2,
    'Log_ps1.log'
)
ps3 = PhaseSensor(
    find_port('PS3'),
    3,
    'Log_ps1.log'
)

# Test if connections work
print('Loop testing open connection to multiple boards.')
for _ in range(10):
    # switch random valve
    pin = random.choice(pins)
    asyncio.run(myValves.switch_valve(pin))
    # read signal from phase sensors
    print(ps1.get_phase())
    print(ps2.get_phase())
    print(ps3.get_phase())


# Create coroutines to read phase sensors
async def phase_sensor_one():
    phase = ps1.get_phase()
    await asyncio.sleep(0.250)
    print(f'PS1: {phase}')


async def phase_sensor_two():
    phase = ps2.get_phase()
    await asyncio.sleep(0.250)
    print(f'PS1: {phase}')


async def phase_sensor_three():
    phase = ps3.get_phase()
    await asyncio.sleep(0.250)
    print(f'PS1: {phase}')


async def phase_sensors_bundle():
    await asyncio.gather(
        phase_sensor_one(),
        phase_sensor_two(),
        phase_sensor_three()
    )

print('Loop testing concurrent reading of multiple phase sensors.')
for _ in range(10):
    asyncio.run(phase_sensors_bundle())
