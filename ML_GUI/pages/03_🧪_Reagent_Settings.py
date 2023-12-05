""" Reagent Settings

This file is automatically activated by running 'streamlit run 🏡_Home.py'.

The different reagents and their corresponding type is filled out here. The types are used to set up
the variable space of the machine learning model (Bayesian Optimization). The number of vials for each
reagent is defined and an excel-file is generated. The Liquid Handler has to be filled out according
to the excel-file. This file will be found in the folder generated under 'User Settings'.

Author: Pauline Tenblad
"""

import streamlit as st
import numpy as np
from PIL import Image
import pandas as pd
import seaborn as sns
import xlsxwriter
import os
from pathlib import Path
from math import ceil

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

# ------------------------------------------------- Number of reagents -------------------------------------------------
# Slider for the number of reagent
st.subheader('Number of reagents')
st.session_state['number_of_reagents'] = st.slider(
    label='Set the number of different reagents to be loaded in the Liquid Handler (excl. solvent):',
    min_value=1,
    max_value=29,
    value=st.session_state['number_of_reagents'],
    step=1,
    help='Slide to select the number of reagent to be loaded in the Liquid Handler',
)
# st.session_state['number_of_reagents'] = number_of_reagents
st.markdown('_____')

# Text fields to insert the name of the reagent
#   (the loop dynamically adapts the number of fields)
st.subheader('Names of reagents')

st.write('<style>div.row-widget.stRadio > div{flex-direction:row;justify-content: left;} </style>',
         unsafe_allow_html=True)  # Radio button, horizontal stile
# st.write('<style>div.st-bf{flex-direction:column;} div.st-ag{font-weight:bold;padding-left:2px;}</style>',
#          unsafe_allow_html=True)

for i in range(st.session_state['number_of_reagents']):
    col1, col2 = st.columns(2)
    st.session_state[f'reagent_name_{i}'] = col1.text_input(
        label=f'Insert the name for reagent number {i + 1}:',
        placeholder='e.g., cyclohexane',
        value=st.session_state[f'reagent_name_{i}']
    )

    available_parameters = ['limiting_reagent', 'excess_reagent', 'catalyst', 'base', 'co-catalyst']
    parameter_index = available_parameters.index(st.session_state[f'parameter_type_reagent_{i}'])
    st.session_state[f'parameter_type_reagent_{i}'] = col2.radio('Parameter Type:',
                                                                 available_parameters,
                                                                 index=parameter_index,
                                                                 key=f'radio_parameter_type_{i}')

st.markdown('_____')

# -------------------------------------- Reagent Concentration and Volumes ---------------------------------------------
st.subheader('reagent concentrations and volumes')
reagent_concentrations = [0]
# Set up layout with columns

tot_number_of_solutions = st.session_state['number_of_reagents'] + 1  # 1 solvent and X reagent

columns_per_row = ceil(tot_number_of_solutions / 3)  # round up

row1_columns = st.columns(columns_per_row)
row2_columns = st.columns(columns_per_row)
row3_columns = st.columns(columns_per_row)
rows = [row1_columns, row2_columns, row3_columns]

with row1_columns[0]:
    st.markdown(f'**Solvent**')
    st.session_state['2mL_vials_solution'] = st.slider(
        label='Set the number of 2 mL vials:',
        min_value=0,
        max_value=int(16 * 4 / (st.session_state['number_of_reagents'] + 1)),  # ensure total < available spots
        step=1,
        value=st.session_state['2mL_vials_solution'],
        help=f'Slide to set the number of 2 mL vials filled with the solution.'
             f' NOTE: Vials are assumed full (manually edit the Excel file for partial filling).',
    )

    st.session_state['4mL_vials_solution'] = st.slider(
        label='Set the number of 4 mL vials:',
        min_value=0,
        max_value=int(11 * 4 / (st.session_state['number_of_reagents'] + 1) - 1),
        step=1,
        value=st.session_state['4mL_vials_solution'],
        help=f'Slide to set the number of 2 mL vials filled with the solution.'
             f' NOTE: Vials are assumed full (manually edit the Excel file for partial filling).',
    )

# Fill columns (the loop dynamically adapts the number of fields)
for i in range(1, st.session_state['number_of_reagents'] + 1):
    with rows[i//columns_per_row][i % columns_per_row]:
        if st.session_state[f'reagent_name_{i-1}'] == '':
            st.markdown(f'**reagent {i}**')
        else:
            st.markdown(f'**{st.session_state[f"reagent_name_{i-1}"]}**')
        st.session_state[f'reagent_concentration_{i-1}'] = st.text_input(
            label=f'Indicate the concentration [mM]:',
            value=st.session_state[f'reagent_concentration_{i-1}'],
            placeholder=f'Concentration of {st.session_state[f"reagent_name_{i-1}"]} in mM',
            key=f'text_input_reagent_concentration_{i-1}'
        )
        reagent_concentrations.append(
            st.session_state[f'reagent_concentration_{i-1}']
        )

        st.session_state[f'2mL_vials_{i-1}'] = st.slider(
            label='Set the number of 2 mL vials:',
            min_value=0,
            max_value=int(16 * 4 / (st.session_state['number_of_reagents'] + 1)),  # ensure total < available spots
            step=1,
            value=st.session_state[f'2mL_vials_{i-1}'],
            key=f'text_input_2mL_vials_{i-1}',
            help=f'Slide to set the number of 2 mL vials filled with {st.session_state[f"reagent_name_{i-1}"]}.'
                 f' NOTE: Vials are assumed full (manually edit the Excel file for partial filling).',
        )

        st.session_state[f'4mL_vials_{i-1}'] = st.slider(
            label='Set the number of 4 mL vials:',
            min_value=0,
            max_value=int(11 * 4 / (st.session_state['number_of_reagents'] + 1) - 1),  # ensure total < available spots
            step=1,
            value=st.session_state[f'4mL_vials_{i-1}'],
            key=f'text_input_4mL_vials_{i-1}',
            help=f'Slide to set the number of 4 mL vials filled with {st.session_state[f"reagent_name_{i-1}"]}.'
                 f' NOTE: Vials are assumed full (manually edit the Excel file for partial filling).',
        )

st.markdown('---')

# Panel with all combined information to double-check
with st.expander('Summary of input information'):
    st.write('The complete list of reagent names is:')
    st.markdown(f'- **Solvent**, '
                f'`{st.session_state[f"2mL_vials_solution"]}x` 2 mL vials, '
                f'`{st.session_state[f"4mL_vials_solution"]}x` 4 mL vials')

    for i in range(st.session_state['number_of_reagents']):
        st.markdown(
            f'- **{st.session_state[f"reagent_name_{i}"]}**, '
            f'`{st.session_state[f"reagent_concentration_{i}"]} mM` solution, '
            f'`{st.session_state[f"2mL_vials_{i}"]}x` 2 mL vials, '
            f'`{st.session_state[f"4mL_vials_{i}"]}x` 4 mL vials, '
            # f'`{st.session_state[f"reagent_price_{i}"]}` €/mmol'
        )
    st.write('')
st.markdown('---')

# ----------------------------------------------- Generate Excel file --------------------------------------------------
st.subheader('Generate Excel file')

# @st.cache(suppress_st_warning=True)
path = os.path.join(PATH_PLATFORM_DATA, st.session_state['user_name'], st.session_state['experiment_name'], f"{st.session_state['experiment_name']}_LH_vial_positions.xlsx")


def make_sample_info_excel_file(path_):
    # Make sample name lists for the two racks

    # Create list of the 4ml vials
    # Naming convention: (name of reagent)-(index for vials containing the same reagent)_(concentration)_4
    samples_list_4 = []
    for i in range(st.session_state[f"4mL_vials_solution"]):
        samples_list_4.append(
            f'Solvent-{i}_0_4'
        )
    for i in range(st.session_state['number_of_reagents']):
        for j in range(st.session_state[f"4mL_vials_{i}"]):
            samples_list_4.append(
                f'{st.session_state[f"reagent_name_{i}"]}-{j}_{st.session_state[f"reagent_concentration_{i}"]}_4'
            )

    # Create list of the 2ml vials
    # Naming convention: (name of reagent)-(index for vials containing the same reagent)_(concentration)_4
    samples_list_2 = []
    for i in range(st.session_state[f"2mL_vials_solution"]):
        samples_list_2.append(
            f'Solvent-{i + st.session_state[f"4mL_vials_solution"]}_0_2'
        )
    for i in range(st.session_state['number_of_reagents']):
        for j in range(st.session_state[f"2mL_vials_{i}"]):
            samples_list_2.append(
                f'{st.session_state[f"reagent_name_{i}"]}-{j + st.session_state[f"4mL_vials_{i}"]}_{st.session_state[f"reagent_concentration_{i}"]}_2'
            )

    # Create list of the variable parameter types and fill it with the reagent names
    variable_parameters = {
        'Solvent': ['Solvent'],
        'limiting_reagent': [],
        'excess_reagent': [],
        'catalyst': [],
        'base': [],
        'co-catalyst': [],
    }
    for i in range(st.session_state['number_of_reagents']):
        variable_parameters[st.session_state[f'parameter_type_reagent_{i}']].append(
            st.session_state[f'reagent_name_{i}'])
    for key, variable in variable_parameters.copy().items():  # Then remove those that are empty
        if not variable:
            variable_parameters.pop(key)

    # Generate Excel file
    # (this creates a new file, it does NOT fill a template)
    # A. Reproduce the template
    # 1. create file
    workbook = xlsxwriter.Workbook(path_)
    worksheet = workbook.add_worksheet()
    worksheet.set_column('A:A', 10)  # reduce column A width
    worksheet.set_column('B:E', 21)  # reduce column A width
    worksheet.set_column('F:F', 10)  # reduce column F width
    worksheet.set_column('G:K', 21)  # reduce column F width
    for row in range(35):
        worksheet.set_row(row, 22)  # adjust row height
    # 2. add title
    title_format = workbook.add_format({
        'font_size': 18,
        'font_name': 'Arial',
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'font_color': 'black',
    })
    worksheet.merge_range('A2:K3', 'Sample table in GX-241', title_format)
    # 3. add warning on sample name formatting
    warning_format = workbook.add_format({
        'font_size': 12,
        'font_name': 'Arial',
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'font_color': 'red',
    })
    worksheet.merge_range(
        'A4:K5',
        'Tips: Fill in the information of your samples in this format: sample name-i_concentration(mM)_volume(mL). '
        'If there are multiple bottles of the same sample, name the sample as name-i (i=0,1,2...).',
        warning_format
    )
    # 4. table labels
    small_label = workbook.add_format({
        'font_size': 15,
        'font_name': 'Arial',
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'font_color': 'black',
    })
    worksheet.write('B7', '338S', small_label)
    worksheet.write('G7', '335S', small_label)
    worksheet.write('B27', 'Sample Name', small_label)
    # 5. borders of the tables
    border_line = workbook.add_format({
        'font_size': 15,
        'font_name': 'Arial',
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'font_color': 'black',
        'border': 2,
    })
    # 338S
    for row in range(7, 23):
        for column in range(1, 5):
            worksheet.write(row, column, '', border_line)
    # 335S
    for row in range(7, 19):
        for column in range(6, 10):
            worksheet.write(row, column, '', border_line)
    # names
    for row in range(27, 29):
        for column in range(1, 10):
            worksheet.write(row, column, '', border_line)
    # 6. black out the cleaning cell
    grey_bkgrnd = workbook.add_format({
        'font_size': 15,
        'font_name': 'Arial',
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#808080',
        'border': 2,
    })
    worksheet.write('G19', '', grey_bkgrnd)

    # B. Fill in the information
    fill_sequence_2 = []  # 338S
    for row in range(7, 23):
        for column in range(1, 5):
            fill_sequence_2.append({'row': row, 'column': column})
    fill_sequence_4 = []  # 335S
    for row in range(7, 19):
        for column in range(6, 10):
            fill_sequence_4.append({'row': row, 'column': column})
    fill_sequence_names = []
    for column in range(1, 10):
        fill_sequence_names.append({'row': 28, 'column': column})

    sample_name_format = workbook.add_format({
        'font_size': 12,
        'font_name': 'Arial',
        'bold': False,
        'align': 'center',
        'valign': 'vcenter',
        'border': 2,
    })
    # 338S
    for k in range(len(samples_list_2)):
        worksheet.write(
            fill_sequence_2[k]['row'],
            fill_sequence_2[k]['column'],
            samples_list_2[k],
            sample_name_format,
        )
    # 335S
    for j in range(len(samples_list_4)):
        worksheet.write(
            fill_sequence_4[j]['row'],
            fill_sequence_4[j]['column'],
            samples_list_4[j],
            sample_name_format,
        )
    # names
    sample_title_format = workbook.add_format({
        'font_size': 12,
        'font_name': 'Arial',
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'border': 2,
    })

    for t, (key, variable) in enumerate(variable_parameters.items()):
        worksheet.write(
            fill_sequence_names[t]['row'] - 1,
            fill_sequence_names[t]['column'],
            key,
            sample_title_format,
        )
        for s in range(len(variable)):
            worksheet.write(
                fill_sequence_names[t]['row'] + s,
                fill_sequence_names[t]['column'],
                variable[s],
                sample_name_format,
            )

    # C. close file
    workbook.close()

    # Confirm execution
    st.success('Excel file successfully generated!')


# Excel experiment_name and generation
button = st.button(
    label='Generate Excel file',
    # on_click=allowed_to_click,
    # args=(path,),
)

columns2 = st.columns([1, 1])
if button:
    solution_names_ok = False
    for i in range(st.session_state['number_of_reagents']):
        if st.session_state[f'reagent_name_{i}'] == '':
            solution_names_ok = False  # If a name not filled in, the reagent_names are set to false again
            break  # and the loop is broken
        else:
            solution_names_ok = True  # This will only stay True if every reagent is filled in

    if not solution_names_ok:
        st.markdown('***Please fill in the names of the reagents before generating the excel file***')

    if st.session_state['experiment_name'] == '':
        st.markdown('***Please fill in the experiment_name before generating the excel file***')

    if solution_names_ok and st.session_state['experiment_name'] != '':  # If everything filled in correctly
        make_sample_info_excel_file(path)  # Create excel file and then display it here

        cm = sns.light_palette("green", as_cmap=True)  # colormap for background
        try:
            # 338S
            df_338s = pd.read_excel(
                # f'{st.session_state["user_name"]}/{st.session_state["experiment_name"]}',
                path,
                engine='openpyxl',
                usecols='B:E',
                skiprows=6,
                nrows=16,
                names=['0', '1', '2', '3'],
            )
            df_338s = df_338s.fillna('-')
            # df_338s.style.background_gradient(cmap=cm)  # apply background colors
            # Display sample map
            with columns2[0]:
                st.markdown('**338S**')
                st.table(df_338s)
                # st.dataframe(df_338s.style.background_gradient(cmap=cm))

            # 335S
            df_335s = pd.read_excel(
                # f'{st.session_state["user_name"]}/{st.session_state["experiment_name"]}',
                path,
                engine='openpyxl',
                usecols='G:J',
                skiprows=6,
                nrows=11,
                names=['0', '1', '2', '3'],
            )
            df_335s = df_335s.fillna('-')
            # df_335s.style.background_gradient(cmap=cm)  # apply background colors
            # Display sample map
            with columns2[1]:
                st.markdown('**335S**')
                st.table(df_335s)
                # st.dataframe(df_335s.style.background_gradient(cmap=cm))

        except FileNotFoundError as e:
            st.error(e)

st.markdown('---')
