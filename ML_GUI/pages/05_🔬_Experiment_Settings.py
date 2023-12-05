""" Experiment Settings

This file is automatically activated by running 'streamlit run 🏡_Home.py'.

All extra parameters that are needed to run the platform are filled in here.

Author: Pauline Tenblad
"""

import streamlit as st
import numpy as np
from PIL import Image


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

st.subheader("Experiment Settings")
# Values used by Run_platform.py
st.session_state['reactor_volume'] = st.text_input('Reactor Volume:', value=float(st.session_state['reactor_volume']))
st.session_state['sample_push_volume'] = st.text_input('Sample Push Volume:', value=float(st.session_state['sample_push_volume']))
st.subheader("NMR Settings")
st.session_state['nmr_nucleus'] = st.text_input('NMR Nucleus:', value=st.session_state['nmr_nucleus'])
st.session_state['integration_calibration'] = st.text_input('Integration Calibration:', value=float(st.session_state['integration_calibration']))
st.session_state['PulseAngle'] = st.text_input('Pulse Angle:', value=st.session_state['PulseAngle'])
st.session_state['Number'] = st.text_input('Number:', value=st.session_state['Number'])
st.session_state['RepetitionTime'] = st.text_input('Repetition Time:', value=st.session_state['RepetitionTime'])
st.session_state['AcquisitionTime'] = st.text_input('Acquisition Time:', value=st.session_state['AcquisitionTime'])
st.session_state['centreFrequency'] = st.text_input('centre Frequency:', value=st.session_state['centreFrequency'])
st.session_state['decouplePower'] = st.text_input('decouple Power:', value=st.session_state['decouplePower'])