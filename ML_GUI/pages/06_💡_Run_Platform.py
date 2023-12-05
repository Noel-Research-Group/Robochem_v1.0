""" Run Platform

This file is automatically activated by running 'streamlit run 🏡_Home.py'.

If all parameters are filled in correctly and all necessary files are located in the right place, the platform can be
run. The platform can be run by pressing the run button on the Run Platform page. This will call the
run_optimization_from_gui.py file which will call the Dragonfly_BO.py file which in turn will use os.popen to run the
run_platform.py file in the Platform_ folder.

In between each run, the new results will be displayed. This by reading the figures named figure_hypervolyme.png and
figure_objectives.png.

Author: Pauline Tenblad
"""

import streamlit as st
import numpy as np
from PIL import Image
import os
import json
import time
import subprocess
# --------------------------------------------- Streamlit page setup ---------------------------------------------------
st.set_page_config(
    layout='wide',
    initial_sidebar_state='expanded'
)

# Title of the main page
display = Image.open('utils/NRG_logo.png')
display = np.array(display)
col1, col2 = st.columns([2, 1])
col1.title('RoboChem Platform')
col2.image(display, width=200)
st.markdown('_____')

# ------------------------------------------------- Run the platform ---------------------------------------------------
st.subheader('Run platform')
objectives_dict = {'yield': ['yield'],  # Single objective
                   'throughput': ['throughput'],  # Single objective
                   'yield & throughput': ['yield', 'throughput'],  # Multi objective
                   'yield & price': ['yield', 'price'],  # Multi objective
                   'throughput & price': ['throughput', 'price'],  # Multi objective
                   'yield & throughput & price': ['yield', 'throughput', 'price']}

# MAKE sure that all needed files exists
PATH_EXPERIMENT = os.path.join(os.path.expanduser("~"), "Platform_Data",
                                  st.session_state['user_name'], st.session_state['experiment_name'])
run_platform = True
if st.session_state['use_previous_runs'] == 'Yes':
    path_json = os.path.join(PATH_EXPERIMENT, f"{st.session_state['experiment_name']}_results.json")
    if not os.path.exists(path_json):
        run_platform = False
        st.markdown('***Trying to run from previous experiments but no json file available***')

path_processing_file = os.path.join(PATH_EXPERIMENT, "processing_file.qs")
if not os.path.exists(path_processing_file):
    run_platform = False
    st.markdown('***Processing file not added to experiment folder. '
                'Please add this folder named "processing_file.qs" before running the experiments***')

path_LH = os.path.join(PATH_EXPERIMENT, f"{st.session_state['experiment_name']}_LH_vial_positions.xlsx")
if not os.path.exists(path_LH):
    run_platform = False
    st.markdown('***Excel file containing the vial positions used by the Liquid Handler has not been generated***')

# st.write(st.session_state['variable_space'])
if run_platform:

    experimental_setup = {
        # Values used by Dragonfly_BO
        'variables': st.session_state['variable_space'],
        'num_init': st.session_state['nr_init'],  # number of initialization experiments
        'num_total': st.session_state['nr_init'] + st.session_state['nr_explor'],  # number of total experiments to perform
        'objectives': objectives_dict[st.session_state['objective']],
        'previous_runs': st.session_state['use_previous_runs'],  # True or False
        'dict_filename': PATH_EXPERIMENT + f"\\{st.session_state['experiment_name']}_results.json",

        # Values used by Run_platform.py
        'reactor_volume': float(st.session_state['reactor_volume']),
        'sample_information_filename': PATH_EXPERIMENT + f"\\{st.session_state['experiment_name']}_LH_vial_positions.xlsx",

        # From Run_platform.py
        'exp_name': st.session_state['experiment_name'],  # NMR Control loop > NMR_loop.py
        'processing_filename': PATH_EXPERIMENT + "\\processing_file.qs",
        # NMR Control loop > NMR_processing.py
        'sample_push_volume': float(st.session_state['sample_push_volume']),  # any large volume for when PS route active (Pumps_Valves_PS_MFC_LiquidHandler.py)

        # NMR Settings and Processing
        'nmr_nucleus': st.session_state['nmr_nucleus'],
        'nmr_settings': {"PulseAngle": st.session_state['PulseAngle'],
                     "Number": st.session_state['Number'],
                     "RepetitionTime": st.session_state['RepetitionTime'],
                     "AcquisitionTime": st.session_state['AcquisitionTime'],
                     "centreFrequency": st.session_state['centreFrequency'],
                     "decouplePower": st.session_state['decouplePower']
                     },
        'integration_calibration': float(st.session_state['integration_calibration'])  # M/int
    }

    # Serializing json
    with open('../experimental_setup.json', 'w') as outfile:
        json.dump(experimental_setup, outfile, indent=4)

    if st.button('Run platform'):
        # original command commented out that used depreciated os.popen
        # os.popen('..\\ML_GUI\\venv\\Scripts\\activate && python ..\\ML_GUI\\run_optimization_from_gui.py', 'w')
        # run optimization as a separate thread
        # setting up the command 'conda run -n robochem_crossplatform python ..\\ML_GUI\\run_optimization_from_gui.py'
        # cmd_args = ['conda', 'run', '-n', 'robochem_gui', 'python', '..\\ML_GUI\\run_optimization_from_gui.py']
        cmd_args = ['python',
                    '..\\ML_GUI\\run_optimization_from_gui.py']
        # sending the command to a new thread
        # NOTE: 1. despite online advice shell must be set to True for the command to find the python file
        # NOTE: 2. the stdin and stdout must be linked to the subprocess.PIPE variable for the command to be sent
        proc = subprocess.Popen(cmd_args,
                                # stdin=subprocess.PIPE,
                                # stdout=subprocess.PIPE,
                                shell=True)
        from PIL import Image

        # When this is run from Streamlit, the figured displayed has to be cleared!
        with Image.open('Campaign has started.png') as image:
            # Save the image as a PNG to the destination file
            image.save('figure_hypervolume.png', 'PNG')
            image.save('figure_objectives.png', 'PNG')

        col1, col2 = st.columns(2)

        placeholder_objectives = col1.empty()
        placeholder_hypervolume = col2.empty()
        while True:  # Update the progress images after each run
            placeholder_objectives .image('figure_objectives.png')
            placeholder_hypervolume.image('figure_hypervolume.png')
            time.sleep(10)