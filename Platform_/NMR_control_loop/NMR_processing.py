"""
Aidan Slattery
Noël Research Group
Van 't Hoff Institute for Molecular Sciences (HIMS)
Universiteit van Amsterdam (UvA)

Functions to call the Spinsolve NMR class and automate the processing
"""

import time
import os
# from Spinsolve_NMR.Spinsolve_NMR import *
from phase_sensor_CSV_naming import get_your_abs_project_path
import pandas as pd
from Phase_sensors.Phase_sensor_detection import ps_data_filename
from pathlib import Path
import json

# Constants
SETUP_INFO_JSON = '../experimental_setup.json'
with open(SETUP_INFO_JSON) as json_file:
    experimental_setup = json.load(json_file)

PROCESSING_FILENAME = experimental_setup["processing_filename"]
NMR_CALIBRATION = experimental_setup["integration_calibration"]


class NMR_Process:
    def __init__(self, conc_theo):
        '''
        NMR_Process is the class used to process the NMR data, however by process we mean the calculation of the target
        variables used in the BO-optimisation. The Actual processing of the NMR spectrum, consisting in phasing, baselining
        and integration is done by Mestrenova under control from Spinsolve.

        :param conc_theo: Float, value of the theoretical concentration of the product in the sample.
        '''

        # initialise class attributes
        self.list = None
        self.nmr_filename = None
        self.conc_theo = conc_theo
        self.integration = []
        # self.settings_csv = get_your_abs_project_path() + \
        #                '\\NMR_control_loop\\NMR_Settings.csv'
        # self.settings = pd.read_csv(self.settings_csv)


    def get_integration(self):
        """
        Function reads the integration value yielding from the Mestrenova analysis, and stores it in the class attribute
        self.integration
        :return:
        """

        # spinsolve = Spinsolve(mysql_reader=None)
        # spinsolve.connect()
        # asyncio.run(spinsolve.run_nmr())

        # gets the path of the working directory to find the path of the NMR data
        path = (
            get_your_abs_project_path()
        )
        # set-up the path of the processed files
        processing_files = path + '\\NMR_control_loop\\processing_files\\'
        processing_path = experimental_setup["processing_filename"]
        process = "ProcessReaction"
        system_string = (f'cmd /c ""C:/Program Files/Mestrelab Research '
                         f'S.L/MestReNova/MestReNova.exe" {processing_path} '
                         f'-sf {process}"')


        # If sample is a reaction solution run reaction processing
        os.system(system_string)
        time.sleep(1)
        # read the integration value from file
        with open(f'{processing_files}last_integral.txt') as f:
            # integration = float(f.readline())
            integration_value = f.read()
            print(f'int: {integration_value}')

        # print(integration)
        # parse integration value
        self.list = integration_value.split('\n')
        self.list.pop()


        # integration = float(self.list[0])
        # for i in range(len(self.list)):
        #     self.integration[i] = float(self.list[i])

        return self.list

    def initialize_nmr_csv(self):
        '''
        Function initialises the csv file where the target values will be stored.
        :return:
        '''
        # make a dataframe to store the processed NMR data
        nmr_data_processed = pd.DataFrame(columns=['Experiment',
                                                   'Integration (Product)',
                                                   'Yield'])

        # get the filename of the processed data
        self.nmr_filename = (
            get_your_abs_project_path()
            + '\\NMR_DATA'
            + '\\NMR_DATA_PROCESSED'
            + f'\\Processed_NMR_data_{ps_data_filename("PS1")[-24:-8]}.csv'
        )
        filepath = Path(self.nmr_filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        # make the CSV file in the chosen directory
        nmr_data_processed.to_csv(
            filepath,
            mode='w',
            header=True,
            index=False,
        )

    def export_NMR_data(self, integration):
        '''
        Function appends a row to the csv file containing the integration value and the nmr data for the current experiment
        :param integration: float, value of the absolute integration of the relevant peak yielding from Mestrenova
        :return: None
        '''

        # int prod = value obtained and int standard = previous value from
        # get the integration value, parsed form Mestrenova
        integration_product = integration[0]

        # get the name of the experiment
        experiment_name = f'{ps_data_filename("PS1")[-24:-8]}'

        # 
        pd_csv = pd.read_csv(self.nmr_filename)
        calculated_yield = self.calculate_yield(
            integration_product
        )

        nmr_data_log = pd.DataFrame(
            {
                'Experiment': experiment_name,
                'Integration (Product)': integration_product,
                'Yield': calculated_yield
            },
            index=[0]
        )
        nmr_data_log.to_csv(
            self.nmr_filename,
            mode='a',
            header=False,
            index=False,
        )


    def calculate_yield(self, integration_product):
        """ Function to calculate the yield from the reaction.
                Mp = ((Ip/np)/Is/ns)*Ms
            :param integration_product: float
                value of the absolute integration of the product peaks passed
                from the NMR
            :param integration_standard: float
                value of the absolute integration of the external standard
                passed from the NMR
            :param conc_theo: float
                theoretical concentration at 100% yield
                }
            :return calculated_yield
                Calculated yield for teh reaction (%)
            """

        conc_reaction = float(integration_product) * NMR_CALIBRATION
        # conc_reaction = (0.418 * self.conc_theo * float(self.list[0])) / \
        #                 float(self.list[1])
        calculated_yield = (conc_reaction/self.conc_theo)*100
        print(f'Yield: {round(calculated_yield, 1)}%')
        return calculated_yield

    def perform_nmr_processing(self):
        '''
        Function gathers the class methods to perform the NMR processing
        :return: float, calculated yield, in fraction.
        '''
        self.initialize_nmr_csv()
        integration = self.get_integration()
        calculated_yield = self.export_NMR_data(integration)
        return calculated_yield


if __name__ == '__main__':
    NMR = NMR_Process(conc_theo=0.15)
    print(NMR.perform_nmr_processing())
