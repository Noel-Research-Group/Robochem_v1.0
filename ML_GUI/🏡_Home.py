""" Home Page

This is the home page of the streamlit app. By running this from the terminal 'streamlit run ??_Home.py' the whole app
is started. In this file the session states used in the whole app is initialized. The session states allow the
parameters/values to be saved in between different pages as well as when a button is clicked. (As this normally will
reset all parameters.)

This Page contains the information of how to set up a campaign.

Author: Pauline Tenblad
"""

import streamlit as st
import numpy as np
from PIL import Image
import os

PATH_PLATFORM_DATA = os.path.join(os.path.expanduser("~"), "Platform_Data")

# Initialization of session states
if 'experiment_name' not in st.session_state:
    st.session_state['experiment_name'] = ''
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = 'Guest'

if 'number_of_reagents' not in st.session_state:
    st.session_state['number_of_reagents'] = 3

if '2mL_vials_solution' not in st.session_state:
    st.session_state['2mL_vials_solution'] = 3
if '4mL_vials_solution' not in st.session_state:
    st.session_state['4mL_vials_solution'] = 3

for i in range(29):
    if f'parameter_type_reagent_{i}' not in st.session_state:
        st.session_state[f'parameter_type_reagent_{i}'] = 'limiting_reagent'

    if f'reagent_name_{i}' not in st.session_state:
        st.session_state[f'reagent_name_{i}'] = ''

    if f'reagent_concentration_{i}' not in st.session_state:
        st.session_state[f'reagent_concentration_{i}'] = 500

    if f'2mL_vials_{i}' not in st.session_state:
        st.session_state[f'2mL_vials_{i}'] = 3
    if f'4mL_vials_{i}' not in st.session_state:
        st.session_state[f'4mL_vials_{i}'] = 3

    if f'reagent_name_{i}_min' not in st.session_state:
        st.session_state[f'reagent_name_{i}_min'] = 0
    if f'reagent_name_{i}_max' not in st.session_state:
        st.session_state[f'reagent_name_{i}_max'] = 0
    if f'reagent_price_{i}' not in st.session_state:
        st.session_state[f'reagent_price_{i}'] = ''

if 'nr_init' not in st.session_state:
    st.session_state['nr_init'] = 5
if 'nr_explor' not in st.session_state:
    st.session_state['nr_explor'] = 15

if 'residence_time_min' not in st.session_state:
    st.session_state['residence_time_min'] = 0
if 'residence_time_max' not in st.session_state:
    st.session_state['residence_time_max'] = 0

if 'eagle_percentage_min' not in st.session_state:
    st.session_state['eagle_percentage_min'] = 0
if 'eagle_percentage_max' not in st.session_state:
    st.session_state['eagle_percentage_max'] = 0

if 'objective' not in st.session_state:
    st.session_state['objective'] = 'yield'


if 'limiting_reagent_min' not in st.session_state:
    st.session_state['limiting_reagent_min'] = 0
if 'limiting_reagent_max' not in st.session_state:
    st.session_state['limiting_reagent_max'] = 0

if 'excess_reagent_min' not in st.session_state:
    st.session_state['excess_reagent_min'] = 0
if 'excess_reagent_max' not in st.session_state:
    st.session_state['excess_reagent_max'] = 0

if 'catalyst_min' not in st.session_state:
    st.session_state['catalyst_min'] = 0
if 'catalyst_max' not in st.session_state:
    st.session_state['catalyst_max'] = 0

if 'base_min' not in st.session_state:
    st.session_state['base_min'] = 0
if 'base_max' not in st.session_state:
    st.session_state['base_max'] = 0

if 'co-catalyst_min' not in st.session_state:
    st.session_state['co-catalyst_min'] = 0
if 'co-catalyst_max' not in st.session_state:
    st.session_state['co-catalyst_max'] = 0

if 'use_previous_runs' not in st.session_state:
    st.session_state['use_previous_runs'] = 'No'

if 'variable_space' not in st.session_state:
    st.session_state['variable_space'] = []

if 'reactor_volume' not in st.session_state:
    st.session_state['reactor_volume'] = 3.9
if 'sample_push_volume' not in st.session_state:
    st.session_state['sample_push_volume'] = 3800
if 'nmr_nucleus' not in st.session_state:
    st.session_state['nmr_nucleus'] = '1D FLUORINE HDEC'
if 'PulseAngle' not in st.session_state:
    st.session_state['PulseAngle'] = 90
if 'Number' not in st.session_state:
    st.session_state['Number'] = 16
if 'RepetitionTime' not in st.session_state:
    st.session_state['RepetitionTime'] = 10
if 'AcquisitionTime' not in st.session_state:
    st.session_state['AcquisitionTime'] = 1.64
if 'centreFrequency' not in st.session_state:
    st.session_state['centreFrequency'] = -80
if 'decouplePower' not in st.session_state:
    st.session_state['decouplePower'] = 0
if 'integration_calibration' not in st.session_state:
    st.session_state['integration_calibration'] = 0.006122  # M/int

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

st.subheader('Instructions')
st.markdown('Welcome to the RoboChem Platform. If this is your first time using the system please read this first.')
st.markdown('- **Step 1**: Select your `user_name` and the `experiment_name`. '
            f'All generated data will be stored as `experiment_name` in `{PATH_PLATFORM_DATA}\\user_name`.\n '
            '- **Step 2**: Set the number of different reagents to be loaded in the Liquid Handler (excluding the '
            'solvent) and name them. For each reagent, mark which type of parameter it is. '
            'Continue by filling in the concentration of the stock-solutions and the number of 2ml and 4ml vials '
            'of each kind. Lastly generate the excel file. Now you may fill in the liquid handler according to the '
            'positions indicated in the excel file.\n '
            '- **Step 3**: Double-check the settings of the NMR and change as needed.\n '
            '- **Step 4**: Pick the optimization goal. Then pick whether to run the platform using previous '
            'experiments for the initialization phase or whether to run new random initial experiments. Set the '
            'number of experiments to run.\n '
            '- **Step 5**:  When the liquid handler is correctly filled and all other settings have been input '
            'and double-checked, go ahead and press **run platform**. After each experiment, the result will be '
            'displayed here and the updated result-file can be found under your user-name as described above.')

st.markdown('_____')
display_1 = Image.open('utils/Platform_Layout.png')
display_2 = Image.open('utils/Platform_IRL.jpg')
display_1 = np.array(display_1)
display_2 = np.array(display_2)
col1, col2 = st.columns([1, 1])
col1.image(display_1)
col2.image(display_2)
st.markdown('_____')