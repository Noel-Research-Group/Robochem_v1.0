""" Machine Learning Settings

This file is automatically activated by running 'streamlit run 🏡_Home.py'.

Here the variable space as needed by the machine learning model (dragonfly Bayesian Optimization) is defined.
The different parameters has been decided in the Reagent Settings already. For each type of parameter, the boundaries
are defined, i.e. the min and max values it can take.

Here it is also decided how many experiments that should be done. How many initial runs and how many extra refinement
runs. It is also possible to start the optimization from previous run files. The corresponding json file has to be saved
in the folder corresponding to current campaign.

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

# --------------------------------------------- Machine Learning Settings ----------------------------------------------
st.subheader('Machine Learning Settings')

# --------------------------------------------- Create Variable space --------------------------------------------------
st.write('Set variable space')

variable_parameters = {
    'limiting_reagent': [],
    'excess_reagent': [],
    'catalyst': [],
    'base': [],
    'co-catalyst': [],
}

for i in range(st.session_state['number_of_reagents']):
    variable_parameters[st.session_state[f'parameter_type_reagent_{i}']].append(st.session_state[f'reagent_name_{i}'])
number_of_columns = 2  # always residence_time and eagle_percentage
if variable_parameters['limiting_reagent']:
    number_of_columns += 1
if variable_parameters['excess_reagent']:
    number_of_columns += 1
if variable_parameters['catalyst']:
    number_of_columns += 1
if variable_parameters['base']:
    number_of_columns += 1
if variable_parameters['co-catalyst']:
    number_of_columns += 1

columns = st.columns(number_of_columns)
column_index = 0

# If variable parameter type present, then set the boundaries
if variable_parameters['limiting_reagent']:
    columns[column_index].markdown('**limiting_reagent**')
    st.session_state['limiting_reagent_min'] = columns[column_index].number_input(
        'min [M]',
        step=0.01,
        value=float(st.session_state['limiting_reagent_min']),
        key='number_input_limiting_reagent_min',
        # step=1e-6,
    )
    st.session_state['limiting_reagent_max'] = columns[column_index].number_input(
        'max [M]',
        step=0.01,
        value=float(st.session_state['limiting_reagent_max']),
        key='number_input_limiting_reagent_max',

    )
    column_index += 1
if variable_parameters['excess_reagent']:
    columns[column_index].markdown('**excess_reagent**')
    st.session_state['excess_reagent_min'] = columns[column_index].number_input(
        'min [eq.]',
        step=0.01,
        value=float(st.session_state['excess_reagent_min']),
        key='number_input_excess_reagent_min'
    )
    st.session_state['excess_reagent_max'] = columns[column_index].number_input(
        'max [eq.]',
        step=0.01,
        value=float(st.session_state['excess_reagent_max']),
        key='number_input_excess_reagent_max'
    )
    column_index += 1
if variable_parameters['catalyst']:
    columns[column_index].markdown('**catalyst**')
    st.session_state['catalyst_min'] = columns[column_index].number_input(
        'min [eq.]',
        step=0.01,
        value=float(st.session_state['catalyst_min']),
        key='number_input_catalyst_min'
    )
    st.session_state[f'catalyst_max'] = columns[column_index].number_input(
        'max [eq.]',
        step=0.01,
        value=float(st.session_state['catalyst_max']),
        key='number_input_catalyst_max'
    )
    column_index += 1
if variable_parameters['base']:
    columns[column_index].markdown('**base**')
    st.session_state['base_min'] = columns[column_index].number_input(
        'min [eq.]',
        step=0.01,
        value=float(st.session_state['base_min']),
        key='number_input_base_min'
    )
    st.session_state['base_max'] = columns[column_index].number_input(
        'max [eq.]',
        step=0.01,
        value=float(st.session_state['base_max']),
        key='number_input_base_max'
    )
    column_index += 1
if variable_parameters['co-catalyst']:
    columns[column_index].markdown('**co-catalyst**')
    st.session_state['co-catalyst_min'] = columns[column_index].number_input(
        'min [eq.]',
        step=0.01,
        value=float(st.session_state['co-catalyst_min']),
        key='number_input_co-catalyst_min'
    )
    st.session_state['co-catalyst_max'] = columns[column_index].number_input(
        'max [eq.]',
        step=0.01,
        value=float(st.session_state['co-catalyst_max']),
        key='number_input_co-catalyst_max'
    )
    column_index += 1

columns[column_index].markdown('**residence_time**')
st.session_state['residence_time_min'] = columns[column_index].number_input(
    'min [s]',
    step=0.01,
    value=float(st.session_state['residence_time_min']),
    key='number_input_residence_time_min'
)
st.session_state['residence_time_max'] = columns[column_index].number_input(
    'max [s]',
    step=0.01,
    value=float(st.session_state['residence_time_max']),
    key='number_input_residence_time_max'
)
column_index += 1

columns[column_index].markdown('**eagle_percentage**')
st.session_state['eagle_percentage_min'] = columns[column_index].number_input(
    'min [%]',
    step=0.01,
    value=float(st.session_state['eagle_percentage_min']),
    key='number_input_eagle_percentage_min'
)
st.session_state['eagle_percentage_max'] = columns[column_index].number_input(
    'max [%]',
    step=0.01,
    value=float(st.session_state['eagle_percentage_max']),
    key='number_input_eagle_percentage_max'
)

variables = []
# we have a problem, as the GUI only passes down the names of the reagents if there's more than one. therefore when
# the platform tries to make a sample it tries to look for a limiting_reagent conc in the sample vials, which ofc doesn't work
# as the sample vials are named 'reagent_name-0'... and not 'limiting_reagent conc'.
# To fix, i'll always add the names of the reagents to the variable space and then modify the condition generation to give out the name
if variable_parameters['limiting_reagent']:
    # if len(variable_parameters['limiting_reagent']) > 1:
    variables.append(
        {'name': 'limiting_reagent', 'type': 'discrete', 'items': variable_parameters['limiting_reagent']})
    variables.append({'name': 'limiting_reagent conc', 'type': 'float', 'min': st.session_state['limiting_reagent_min'],
                      'max': st.session_state['limiting_reagent_max']})
if variable_parameters['excess_reagent']:
    # if len(variable_parameters['excess_reagent']) > 1:
    variables.append({'name': 'excess_reagent', 'type': 'discrete', 'items': variable_parameters['excess_reagent']})
    variables.append({'name': 'excess_reagent equiv', 'type': 'float', 'min': st.session_state['excess_reagent_min'],
                      'max': st.session_state['excess_reagent_max']})
if variable_parameters['catalyst']:
    # if len(variable_parameters['catalyst']) > 1:
    variables.append({'name': 'catalyst', 'type': 'discrete', 'items': variable_parameters['catalyst']})
    variables.append({'name': 'catalyst loading', 'type': 'float', 'min': st.session_state['catalyst_min'],
                      'max': st.session_state['catalyst_max']})
if variable_parameters['base']:
    # if len(variable_parameters['base']) > 1:
    variables.append({'name': 'base', 'type': 'discrete', 'items': variable_parameters['base']})
    variables.append({'name': 'base loading', 'type': 'float', 'min': st.session_state['base_min'],
                      'max': st.session_state['base_max']})
if variable_parameters['co-catalyst']:
    # if len(variable_parameters['co-catalyst']) > 1:
    variables.append({'name': 'co-catalyst', 'type': 'discrete', 'items': variable_parameters['co-catalyst']})
    variables.append({'name': 'co-cat loading', 'type': 'float', 'min': st.session_state['co-catalyst_min'],
                      'max': st.session_state['co-catalyst_max']})
variables.append({'name': 'residence_time', 'type': 'float', 'min': st.session_state['residence_time_min'],
                  'max': st.session_state['residence_time_max']})
variables.append({'name': 'eagle_percentage', 'type': 'float', 'min': st.session_state['eagle_percentage_min'],
                  'max': st.session_state['eagle_percentage_max']})

st.session_state['variable_space'] = variables
st.markdown('---')

# ------------------- Panel with all combined information to double-check ----------------------------------------------
with st.expander('Summary of variable space'):
    st.write('The complete list of variables:')

    if variable_parameters['limiting_reagent']:
        # if len(variable_parameters['limiting_reagent']) > 1:
        f"`- 'name': 'limiting_reagent', 'type': 'discrete', 'items': {variable_parameters['limiting_reagent']}`"
        f"`- 'name': 'limiting_reagent conc', 'type': 'float', 'items': 'min': {st.session_state['limiting_reagent_min']}, 'max': {st.session_state['limiting_reagent_max']}`"
    if variable_parameters['excess_reagent']:
        # if len(variable_parameters['excess_reagent']) > 1:
        f"`- 'name': 'excess_reagent', 'type': 'discrete', 'items': {variable_parameters['excess_reagent']}`"
        f"`- 'name': 'excess_reagent equiv', 'type': 'float', 'items': 'min': {st.session_state['excess_reagent_min']}, 'max': {st.session_state['excess_reagent_max']}`"
    if variable_parameters['catalyst']:
        # if len(variable_parameters['catalyst']) > 1:
        f"`- 'name': 'catalyst', 'type': 'discrete', 'items': {variable_parameters['catalyst']}`"
        f"`- 'name': 'cat loading', 'type': 'float', 'items': 'min': {st.session_state['catalyst_min']}, 'max': {st.session_state['catalyst_max']}`"
    if variable_parameters['base']:
        # if len(variable_parameters['base']) > 1:
        f"`- 'name': 'base', 'type': 'discrete', 'items': {variable_parameters['base']}`"
        f"`- 'name': 'base loading', 'type': 'float', 'items': 'min': {st.session_state['base_min']}, 'max': {st.session_state['base_max']}`"
    if variable_parameters['co-catalyst']:
        # if len(variable_parameters['co-catalyst']) > 1:
        f"`- 'name': 'co-catalyst', 'type': 'discrete', 'items': {variable_parameters['co-catalyst']}`"
        f"`- 'name': 'co-cat loading', 'type': 'float', 'items': 'min': {st.session_state['co-catalyst_min']}, 'max': {st.session_state['co-catalyst_max']}`"
    f"`- 'name': 'residence_time', 'type': 'float', 'items': 'min': {st.session_state['residence_time_min']}, 'max': {st.session_state['residence_time_max']}`"
    f"`- 'name': 'eagle_percentage', 'type': 'float', 'items': 'min': {st.session_state['eagle_percentage_min']}, 'max': {st.session_state['eagle_percentage_max']}`"
    st.write('')

st.markdown('---')

# -------------------------------- Decide objectives and specify run paramters -----------------------------------------
objectives = ('yield',  # Single objective
              'throughput',  # Single objective
              'yield & throughput',  # Multi objective
              )
objective_index = objectives.index(st.session_state['objective'])
st.session_state['objective'] = st.radio('Optimize for:',
                                         objectives,
                                         index=objective_index
                                         )
st.markdown('---')

use_prev_run_alternatives = ['No', 'Yes']
use_prev_run_index = use_prev_run_alternatives.index(st.session_state['use_previous_runs'])
st.session_state['use_previous_runs'] = st.radio('Use previous runs?',
                                                 use_prev_run_alternatives,
                                                 index=use_prev_run_index)
col1, col2 = st.columns([1, 1])
if st.session_state['use_previous_runs'] == 'No':
    st.session_state['nr_init'] = col1.slider(label='Number of initial runs:',
                                              min_value=0,
                                              max_value=10,
                                              step=1,
                                              value=st.session_state['nr_init'],
                                              )

    st.session_state['nr_explor'] = col2.slider(label='Number of exploration/refinement runs:',
                                                min_value=0,
                                                max_value=30,
                                                step=1,
                                                value=st.session_state['nr_explor'],
                                                )

    nr_tot = st.session_state['nr_init'] + st.session_state['nr_explor']
    st.text(f'Total number of runs: {nr_tot}')

else:
    path = os.path.join(PATH_PLATFORM_DATA, st.session_state['user_name'], st.session_state['experiment_name'],
                        f"{st.session_state['experiment_name']}_results.json")
    if os.path.isfile(path):
        col1.write(' ')
        col1.write(f'Previous file found')
    else:
        col1.write(' ')
        col1.write(f"File not found [{st.session_state['experiment_name']}_results.json]")

    st.session_state['nr_explor'] = col2.slider(label='Number of exploration runs:',
                                                min_value=0,
                                                max_value=30,
                                                step=1,
                                                value=st.session_state['nr_explor'],
                                                )

st.markdown('---')
