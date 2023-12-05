""" User Settings

This file is automatically activated by running 'streamlit run 🏡_Home.py'.

Here the user can fill in the name of the user which will create a new folder (if it doesn't already exist)
and the name of the experiments that will be run. All corresponding files will be saved at this location with
the name of the experiments.

Author: Pauline Tenblad
"""

import streamlit as st
import numpy as np
from PIL import Image
import os
from pathlib import Path

DIR_PATH = Path(__file__).parent.absolute()  # Path to parent folder
PATH_PLATFORM_DATA = os.path.join(os.path.expanduser("~"), "Platform_Data")
# os.path.expanduser("~") gives path to C:\Users\$USER$
# os.path.join("A", "B") gives path to A\B
if not os.path.exists(PATH_PLATFORM_DATA):
    os.makedirs(PATH_PLATFORM_DATA)
if not os.path.exists(os.path.join(PATH_PLATFORM_DATA, "Guest")):
    os.makedirs(os.path.join(PATH_PLATFORM_DATA, "Guest"))

# Path to current experiment is:
PATH_PLATFORM_DATA = os.path.join(os.path.expanduser("~"), "Platform_Data")
PATH_USER = os.path.join(PATH_PLATFORM_DATA, st.session_state['user_name'])
PATH_EXPERIMENT = os.path.join(PATH_USER, st.session_state['experiment_name'])
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

# ----------------------------------------------------- User -----------------------------------------------------------
st.subheader('User name')
st.write('')

# Create list with available users, move guest folder to front (default option)
available_users = [name for name in os.listdir(PATH_PLATFORM_DATA)
                   if os.path.isdir(os.path.join(PATH_PLATFORM_DATA, name))]
available_users.remove('Guest')
available_users.insert(0, 'Guest')

col1, col2, col3, col4 = st.columns([10, 2, 10, 28])

# Choose the user
user_index = available_users.index(st.session_state['user_name'])
st.session_state['user_name'] = col1.selectbox('Current user',
                                               available_users,
                                               index=user_index
                                               )

# Add new user if not in list of available users
new_folder = col3.text_input('If your name is not in list, add your name here')
if new_folder != '':
    if not os.path.exists(os.path.join(PATH_PLATFORM_DATA, new_folder)):
        os.makedirs(os.path.join(PATH_PLATFORM_DATA, new_folder))
col3.button('Update user-list')
col2.write('')
col4.write('')
st.markdown('_____')

# ------------------------------------------------ FILENAME ------------------------------------------------------------

st.subheader('Experiment')
col21, col22, col23, col24 = st.columns([10, 2, 10, 28])
st.session_state['experiment_name'] = col21.text_input(
    label=f'Insert the name for the files generated this run:',
    value=st.session_state['experiment_name'],
)

if st.session_state['experiment_name'] != '':
    if not os.path.exists(os.path.join(PATH_USER, st.session_state['experiment_name'])):
        os.makedirs(os.path.join(PATH_USER, st.session_state['experiment_name']))
st.markdown('_____')
