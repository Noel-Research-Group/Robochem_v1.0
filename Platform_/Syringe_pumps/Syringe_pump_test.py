import asyncio
from Syringe_pumps.Syringe_pump import SyringePump
from List_connected_devices import find_port

Pump_C = SyringePump(
    find_port('Syringe_pump_C'),
    38400,
    'Pump_C',
)

# max volume
print(f'Max volume: {float(Pump_C.get_parameter_limits()[1].split(" ")[2])}')

# min volume
print(f'Min volume: {float(Pump_C.get_parameter_limits()[1].split(" ")[3])}')

# max flow rate
print(f'Max flow rate: {float(Pump_C.get_parameter_limits()[1].split(" ")[0])}')

# max volume
print(f'Min flow rate: {float(Pump_C.get_parameter_limits()[1].split(" ")[1])}')

asyncio.run(Pump_C.operate_pump(1000, 1.0))