"""
Diego Pintossi
Noël Research Group
Van 't Hoff Institute for Molecular Sciences (HIMS)
Universiteit van Amsterdam (UvA)

Script to find serial devices connected to the laptop.
"""

import serial.tools.list_ports
from dotenv import load_dotenv
from phase_sensor_CSV_naming import get_your_abs_project_path
import os
dotenv_path = os.path.join(get_your_abs_project_path(), 'Sensitive_data.env')
load_dotenv(dotenv_path)

# map of the equipment
def find_port(device):
    """Function to identify the device given as argument.

    :param device: str
        Name of the device to be identified. It should be one of my_devices.keys
    :return: str
        Name of the serial port connecting to the desired device.
    """
    my_devices = {
        'Syringe_pump_A': os.getenv("SERIAL_N_SYRINGE_PUMP_A"),
        'Syringe_pump_B': os.getenv("SERIAL_N_SYRINGE_PUMP_B"),
        'Syringe_pump_C': os.getenv("SERIAL_N_SYRINGE_PUMP_C"),
        'Pump_A_ultrasonic_detector': os.getenv("SERIAL_N_PUMP_A_ULTRASONIC_DETECTOR"),
        'Pump_B_ultrasonic_detector': os.getenv("SERIAL_N_PUMP_B_ULTRASONIC_DETECTOR"),
        'Pump_C_ultrasonic_detector': os.getenv("SERIAL_N_PUMP_C_ULTRASONIC_DETECTOR"),
        'PS1': os.getenv("SERIAL_N_PS1"),
        'PS2': os.getenv("SERIAL_N_PS2"),
        'PS3': os.getenv("SERIAL_N_PS3"),
        'PS4': os.getenv("SERIAL_N_PS4"),
        'PS5': os.getenv("SERIAL_N_PS5"),
        'PS6': os.getenv("SERIAL_N_PS6"),
        'PS7': os.getenv("SERIAL_N_PS7"),
        'Switch_valves': os.getenv("SERIAL_N_SWITCH_VALVES"),
        'MFC': os.getenv("SERIAL_N_MFC"),
        'Liquid_handler': os.getenv("SERIAL_N_LIQUID_HANDLER"),
        'NMR': None
    }
    
    if device in my_devices.keys():  # check that the device name exists in dict
        ports = serial.tools.list_ports.comports()
        for port, desc, hwid in sorted(ports):
            serial_num = [item for item in hwid.split(' ') if 'SER=' in item]
            if len(serial_num) != 0:
                if serial_num[0][4:] == my_devices[device]:
                    port_name = port
                    # print(f'The port name for {device} is {port_name}.')
                    return port_name
    else:
        print('Device unknown.')


if __name__ == '__main__':
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
        print(f'{port} / {desc} / [{hwid}]')

    print('\n')

    for _ in [
        'Syringe_pump_A',
        'Syringe_pump_B',
        'Syringe_pump_C',
        'Pump_A_ultrasonic_detector',
        'Pump_B_ultrasonic_detector',
        'Pump_C_ultrasonic_detector',
        'PS1',
        'PS2',
        'PS3',
        'PS4',
        'PS5',
        'PS6',
        'PS7',
        'Switch_valves',
        'MFC',
        'Liquid_handler'
    ]:
        print(_, find_port(_))  # expected outcome: COM11 (Diego's UvA laptop)
