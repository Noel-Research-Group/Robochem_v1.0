"""
Pauline Tenblad, Aidan Slattery

Script to run optimization. (WITHOUT USING THE GUI)

This file should be used for both single optimization and for multiple consecutive optimization problems.

In this file, the user should fill in the setup parameters. Each optimization has its own dictionary.
For each optimization a new json file containing this information named 'experimental_setup.json' is generated. This
one overwrites the previous run and as such, the data needed at different places in the code, is all changed from here.

The data that has to be included per run is:
    Values used by Dragonfly_BO:
        variables (the domain the model should optimize over),
        num_init (number of initialization experiments),
        num_total (number of total experiments to perform),
        objectives (for instance 'yield'),
        dict_filename (filename where data for previous runs are stored, and where to store the data),
        previous_runs (whether the model should use previous runs or not [False/True]),

    Values used by Run_platform.py:
        sample_information_filename (Path and name to file used by the liquid handler)

    Values used by NMR Control loop > NMR_loop.py:
        exp_name (experiment name)

    Values used by Control loop > NMR_processing.py:
        processing_filenameNMR (name of file for NMR results)

"""

from Dragonfly_BO import dragonfly_bo
import json

# Parameter setup
# STEP 1: Define the dictionary per experimental setup to be run
A = {
    # Values used by Dragonfly_BO
    'variables': [
        {'name': 'A', 'type': 'float', 'min': 0.1, 'max': 0.2},
        {'name': 'B', 'type': 'float', 'min': 1, 'max': 18},
        {'name': 'catalyst_type', 'type': 'discrete', 'items': ['CatA',
                                                           'CatB']},
        {'name': 'catalyst_loading', 'type': 'float', 'min': 0.01, 'max':
            0.1},
        {'name': 'residence_time', 'type': 'float', 'min': 300, 'max': 900},
        #seconds
        {'name': 'eagle_percentage', 'type': 'float', 'min': 5, 'max': 100}
    ],
    'num_init': 5,  # number of initialization experiments
    'num_total': 25,  # number of total experiments to perform
    'objectives': ['yield'],
    'previous_runs': False,
    'dict_filename': '../AS_example.json',

    # Values used by Run_platform.py
    'reactor_volume': 3.4,
    'sample_information_filename': '/Liquid_Handler/example.xlsx',  # From
    # Run_platform.py
    'exp_name': 'example_1',  # NMR Control loop > NMR_loop.py
    'processing_filename': 'example.qs',  # NMR Control loop > NMR_processing.py
    'sample_push_volume': 10000,  # any large volume for when post reactor PS
    # are on
    # route active (Pumps_Valves_PS_MFC_LiquidHandler.py)


    # NMR Settings and Processing
    'nmr_nucleus': "1D EXTENDED+",
    'nmr_settings': {"PulseAngle": "90",
                     "Number": "16",
                     "RepetitionTime": "15",
                     "AcquisitionTime": "6.4",
                 },
    'integration_calibration': 0.001  # M/int
}

experimental_setups = [A] #add multiple to list if running back-to-back
# optimizations

# STEP 2 : Run each experimental setup consecutively
if __name__ == '__main__':
    for experimental_setup in experimental_setups:
        print(experimental_setup)
        # Serializing json
        with open('../experimental_setup.json', 'w') as outfile:
            json.dump(experimental_setup, outfile, indent=4)

        # Each time dragonfly_bo is called it will in itself call run_platform the number of time that is needed.
        # The information that changes per optimization setup is found in the json file.

        dragonfly_bo(
            experimental_setup['reactor_volume'],
            experimental_setup['variables'],
            experimental_setup['num_init'],
            experimental_setup['num_total'],
            objectives_=experimental_setup['objectives'],
            dict_filename_=experimental_setup['dict_filename'],
            previous_runs_=experimental_setup['previous_runs'],
        )