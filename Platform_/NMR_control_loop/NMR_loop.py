"""
Aidan Slattery
Noël Research Group
Van 't Hoff Institute for Molecular Sciences (HIMS)
Universiteit van Amsterdam (UvA)

This contains the control loop from the reactor to the NMR.



                              [NMR]
                                /\
                                |
                              [PS7]
                                |
--------> [PS5] --------> (Switch-Valves) <--------
                                |                 |
                                |                (T) ------- [syringe pump]
                               \/                 |
                             Waste            Reservoir
"""

from Spinsolve_NMR.Spinsolve_NMR import *
from NMR_control_loop.NMR_processing import NMR_Process
import pandas as pd
import json
from Phase_sensors.Phase_sensor_detection import *
from Phase_sensors.Droplet_identification import identify_reaction_mix
# from Pumps_Valves_PS_MFC_LiquidHandler import SamplePreparation
# from Pumps_valves_MFC_PS_control.Pumps_valves_MFC_PS_control_v2 import PumpsValvesMFCPS
from Syringe_pumps_and_valves_ensemble.Single_pump_and_valve_ensemble import SinglePumpValveEnsemble
from platform_class import Platform
from List_connected_devices import find_port

# Constants
SETUP_INFO_JSON = '../experimental_setup.json'
with open(SETUP_INFO_JSON) as json_file:
    experimental_setup = json.load(json_file)

EXP_NAME = experimental_setup["exp_name"]


class NMRLoop:

    def __init__(self, platform, pump_c, residence_time, chemical_space):
        '''
        Initialisation of the NMR loop, sets up the connection to the rest of the system and finds the correct
        path of the settings file.

        :param platform: instance of class platform_class.Platform, contains the connections to the pumps and valves
        :param pump_c: instance of class Syringe_pumps_and_valves_ensemble.Single_pump_and_valve_ensemble.SinglePumpValveEnsemble
        establishes connection to the C-pump
        :param residence_time: return from the function variable_space.create_variable_space, contains the residence times
        :param chemical_space: return from the function variable_space.create_variable_space, contains the chemical space

        :return: None
        '''
        self.platform = platform
        self.detect_frequency = 0.75
        self.chemical_space = chemical_space
        self.residence_time = residence_time
        self.analyzed_interval = ((self.residence_time * 0.439) + 20)
        # self.settings_csv = get_your_abs_project_path() + \
        #                     '\\NMR_control_loop\\NMR_Settings.csv'
        # self.settings = pd.read_csv(self.settings_csv)
        # switch valves
        self.switch_valves = platform.switch_valves
        # Syringe pump c initialize and set diameter and units
        self.pump_valve = pump_c

        self.pump_A = platform.syringe_pump_a
        self.pump_B = platform.syringe_pump_b
        # self.PumpsValvesMFCPS = PumpsValvesMFCPS(platform)
        # self.SamplePreparation = SamplePreparation(platform)


    async def the_loop(self):
        """This is the loop that runs the NMR-Machine. It calls to Spinsolve,
        which actuates the NMR itself and
        awaits for the processed data to be returned. It then calls to
        NMR_Process which calculates the target variables.
        Wait for phase sensor (PS6) to detect the reaction-droplet. When
        detected, the 4-way switch valve (4B) will change the flow to go
        towards the NMR instead of the waste.
        """

        # A. Loop waiting for droplet at PS6
        await asyncio.sleep(100)
        while True:
            await asyncio.sleep(self.detect_frequency)
            # Check for droplet
            try:
                detected = await identify_reaction_mix(
                    ps_data_filename('PS5'),
                    droplet_data_filename('PS5'),
                    sample_time=self.analyzed_interval,
                )
            except Exception as e:
                print(f'Exception at PS5 detection loop: {e}')
            # Break loop if droplet detected
            if detected:
                break
        print('Droplet at PS6 has triggered 4-way valve ON')
        await self.switch_valves.valve_4_ON_or_C_1()

        # B. Loop waiting for droplet at PS7
        print('Now waiting for droplet in phase sensor 7')
        while True:
            await asyncio.sleep(self.detect_frequency)
            # Check for droplet
            try:
                detected = await identify_reaction_mix(
                    ps_data_filename('PS7'),
                    droplet_data_filename('PS7'),
                    sample_time=self.analyzed_interval,
                )
            except Exception as e:
                print(f'Exception at PS7 detection loop: {e}')
            # Break loop if droplet detected
            if detected:
                break
        await self.switch_valves.valve_3_OFF_or_C_3()
        await self.switch_valves.valve_4_OFF_or_C_3()
        print('Droplet at PS7 has triggered 4-way  OFF')
        # Switch off pump A and pump B
        self.pump_A.stop_pump()
        self.pump_B.stop_pump()
        # Bring slug to NMR probe

        await self.pump_valve.pump_to_analysis(
            volume=100,
            flow_rate=1,
            phase_sensor='PS4',
            detect_sample=True,
            continuous=False
        )

        experiment_name = f'{EXP_NAME}_{ps_data_filename("PS1")[-24:-8]}'
        print(experiment_name)
        # Trigger NMR
        print('NMR triggered')
        await Spinsolve(mysql_reader=None).run_nmr(
            experiment_name=experiment_name,
        )
        print('NMR complete')
        print('Processing NMR')
        # await asyncio.sleep(10)
        # ask NMR_Process to calculate the target values
        nmr_processing = NMR_Process(conc_theo=self.chemical_space[1])
        nmr_processing.perform_nmr_processing()

        # begin cleaning cycle
        print('NMR Processing completed')
        print('Cleaning cycle starting')
        await self.switch_valves.valve_3_OFF_or_C_3()
        await self.switch_valves.valve_4_OFF_or_C_3()
        await self.pump_valve.operate_ensemble(
            volume=2000,
            flow_rate=4.0
        )
        # print('Cleaning cycle completed')
        print('NMR Loop completed')


    async def the_loop_TBADT(self):
        '''
        This is the loop that runs the NMR-Machine. It calls to Spinsolve, which actuates the NMR itself and
        awaits for the processed data to be returned. It then calls to NMR_Process which calculates the target variables.

        This is a slightly modified way to run the platform when TBADT is in
        the catalyst being run. After irradiation TBADT makes a black
        reaction which tricks the phase sensors after the reactor. This works around that

        :return:
        None
        '''
        # Trigger NMR
        # NMR Settings

        experiment_name = f'{EXP_NAME}_{ps_data_filename("PS1")[-24:-8]}'

        # Trigger NMR
        print('NMR triggered')
        # ask Spinsolve to collect a NMR-spectrum with set NMR parameters
        await Spinsolve(mysql_reader=None).run_nmr(
            experiment_name=experiment_name,
        )

        print('NMR complete')
        print('Processing NMR')

        # ask NMR_Process to calculate the target values
        nmr_processing = NMR_Process(conc_theo=self.chemical_space[1])
        nmr_processing.perform_nmr_processing()

        #begin cleaning cycle
        print('NMR Processing completed')
        print('Cleaning cycle starting')
        await self.switch_valves.valve_3_OFF_or_C_3()
        await self.switch_valves.valve_4_OFF_or_C_3()
        await self.pump_valve.operate_ensemble(
            volume=2000,
            flow_rate=4.0
        )
        # print('Cleaning cycle completed')

        print('NMR Loop completed')


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
    pump_C = SinglePumpValveEnsemble(platform)
    chemical_space = [
         'Benzmalonitrile', 0.15000000000000002, 'THF', 9.5, 'TBADT', 0.019999999999999997, 240, 50
    ]
    residence_time = 240
    nmr_loop = NMRLoop(platform, pump_C, residence_time, chemical_space)

