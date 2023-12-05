""" Visualization
This file is used to generate the figures of the result and of the hypervolume.

It uses seaborn for the graphics.

Author:
Aidan Slattery, Pauline Tenblad, April 2023
"""

# Utilities
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pymoo.indicators.hv import HV
import json


# Note! This function is hardcoded for yield and throughput
def get_pandas_dataframe(filename_json, variables, reactor_volume):
    """
    Get a pandas dataframe containing the hypervolume.

    :param filename_json: .json file
        the result of a campaign run on the platform
    :param variables: dict
        the variable space of the bayesian optimization
    :param reactor_volume: float
        the volume of the reactor
    :return: dataframe
        returns a pandas dataframe with the values of the json file and the hypervolume for each run
    """
    max_concentration = variables[0]['max']
    min_residence_time = next(variable['min'] for variable in variables if variable['name'] == 'residence_time')
    max_throughput = (max_concentration * reactor_volume / min_residence_time) * 60 * 60
    max_volume = max_throughput * 100

    with open(filename_json, 'r') as filepointer:
        data_dict = json.load(filepointer)

    # Get the objective values measured so far
    objective_values_list = []
    yield_list = []
    throughput_list = []
    run_list = []
    for i, x in enumerate(data_dict):
        objective_values_list.append([data_dict[x][0][0], data_dict[x][0][1]])
        yield_list.append(data_dict[x][0][0])
        throughput_list.append(data_dict[x][0][1])
        run_list.append(i + 1)

    # Set the reference point to origo
    reference_point = [0, 0]

    # Create a Hypervolume object for the minimization problem
    hv = HV(ref_point=reference_point)

    # Calculate the hypervolume after each run
    hypervolume_list = [0]
    for i in range(len(objective_values_list)):
        if i > 0:  # Need at least two values to get hypervolume calculation
            # Pareto front (Also non pareto front points can be present)
            pareto_front = -np.array(objective_values_list[0:i])
            # Note: Default is minimization so to maximize the values are multiplied with -1.
            hypervolume = hv(np.array(pareto_front)) / max_volume
            hypervolume_list.append(hypervolume)

            # Convert lists into a Pandas dataframe
    data = pd.DataFrame({'run': run_list, 'objective values': objective_values_list,
                         'yield': yield_list, 'throughput': throughput_list,
                         'hypervolume': hypervolume_list})
    return data


def get_hypervolume_visualization(data, figure_name_hypervolume):
    """ Function to get a figure of the development of the hypervolume after each run

    :param data: dataframe
        pandas dataframe with parameters, result and hypervolume per run
    :param figure_name_hypervolume: str
        the name of the figure
    :return:
        generates a figure ot the hypervolume after each run
    """
    # Set a theme for Seaborn
    sns.set(font_scale=1.6, style='ticks', font='Calibri')
    plt.figure(figsize=(6, 6))

    # Set plot title and labels
    plt.title('Hypervolume', fontsize=27, fontweight='bold')
    plt.xlabel('Run', fontweight='bold')
    plt.ylabel('Hypervolume', fontweight='bold')

    sns.lineplot(data=data, x=data['run'], y=data['hypervolume'],
                 color='#002060', linewidth=3,
                 marker=None, zorder=1)

    # Create a scatter plot with customized circle markers
    sns.scatterplot(data=data, x=data['run'], y=data['hypervolume'],
                    marker='o', s=80, edgecolor='#002060', linewidth=1.5,
                    facecolor='#F39000', zorder=2)

    # Set figure size and font weight
    plt.rcParams['font.weight'] = 'bold'
    plt.ylim(0, 1)

    # Save the figure
    plt.savefig(figure_name_hypervolume, dpi=600)


def get_result_per_run_multi_objectives_visualization(data, figure_name_objectives):
    """ Function to get a figure of the result after each run
    Graphing for GUI for multi objective function
    OBS: This is hardcoded for yield and throughput!

    :param data: dataframe
        pandas dataframe with parameters, result and hypervolume per run
    :param figure_name_hypervolume:
        the name of the figure
    :return:
        generates a figure ot the result after each run
    """

    # Set a theme for Seaborn
    sns.set(font_scale=1.6, style='ticks', font='Calibri')
    plt.figure(figsize=(6, 6))

    # Set plot title and labels
    plt.title('Results', fontsize=27, fontweight='bold')
    plt.xlabel('Throughput (mmol/hr)', fontweight='bold')
    plt.ylabel('Yield (%)', fontweight='bold')

    # Create a scatter plot with customized circle markers
    sns.scatterplot(data=data, x=data['throughput'], y=data['yield'],
                    marker='o', s=250, edgecolor='#002060', linewidth=2.5,
                    facecolor='#F39000', zorder=2)

    # Set figure size and font weight
    plt.rcParams['font.weight'] = 'bold'
    plt.ylim(0, 105)
    # Save the plot
    plt.savefig(figure_name_objectives, dpi=600)


def get_result_per_run_single_objective_visualization(data, objective, variables, reactor_volume, total_number_of_runs,
                                                      figure_name_objectives):
    """
    Graphing for GUI for single objective function
    :param data: dataframe
        pandas dataframe with parameters, result and run
    :param objective: str
        'yield' or 'throughput'
    :param variables: list
        vars for calculating max values
    :param reactor_volume: float
        reactor volume
    :param total_number_of_runs: int
        total number of runs for the campaign
    :param figure_name_objectives: string
        the name of the figure
    :return:
    """

    df_marker = data.copy()  # for the markers, dont start at 0,0
    # Add a row with 0 at the top of the dataframe, and use this for the line
    df_line = data.copy()
    df_line.loc[-1] = 0
    df_line.index = df_line.index + 1
    df_line = df_line.sort_index()

    # Set all the variables for plots
    plt.rcParams['font.weight'] = 'bold'
    plt.figure(figsize=(9, 6))
    # Set a theme for Seaborn
    sns.set(font_scale=1.6, style='ticks', font='Calibri')

    line_color = '#002060'
    marker_color = '#F39000'

    # Create a line plot without markers
    sns.lineplot(data=df_line, x='run', y=objective, color=line_color, linewidth=3,
                 marker=None, zorder=1)

    # Create a scatter plot with customized circle markers
    sns.scatterplot(data=df_marker, x='run', y=objective, marker='o', s=300,
                    edgecolor=line_color,
                    linewidth=2.5, facecolor=marker_color, zorder=2)

    # Set plot title and labels
    plt.title('Single-Objective Optimization Using Robochem', fontsize=27,
              fontweight='bold')
    plt.xlabel('Run', fontweight='bold')

    # Show the plot
    if objective == 'yield':
        plt.ylabel('Yield (%)', fontweight='bold')
        plt.ylim(0, 105)
    elif objective == 'throughput':
        plt.ylabel('Throughput (mmol)', fontweight='bold')
        max_concentration = variables[0]['max']
        min_residence_time = next(variable['min'] for variable in variables if variable['name'] == 'residence_time')
        max_throughput = (max_concentration * reactor_volume / min_residence_time) * 60 * 60
        plt.ylim(0, max_throughput)
    plt.xlim(0, total_number_of_runs + 1)

    plt.savefig(figure_name_objectives, dpi=600)
    return


def get_visualization(filename_json, variables, reactor_volume, figure_name_hypervolume, figure_name_objectives,
                      objectives, total_number_of_runs):
    """

    :param filename_json: .json file
        the result of a campaign run on the platform
   :param variables: list
        vars for calculating max values
    :param reactor_volume: float
        reactor volume
    :param figure_name_hypervolume: str
        the name of the figure
    :param figure_name_objectives: str
        the name of the figure
    :param objective: str
        'yield' or 'throughput'
    :param total_number_of_runs: int
        total number of runs for the campaign
    :return:
    """
    data = get_pandas_dataframe(filename_json, variables, reactor_volume)
    if len(objectives) > 1: # Multi-objective Optimization
        get_hypervolume_visualization(data, figure_name_hypervolume)
        get_result_per_run_multi_objectives_visualization(data, figure_name_objectives)
    else:  # Single-objective Optimization
        get_result_per_run_single_objective_visualization(data, objectives[0], variables, reactor_volume,
                                                          total_number_of_runs, figure_name_objectives)


if __name__ == '__main__':
    # Note: The following code is an example of how to run the visualization
    filename_json = '../example.json'
    objectives = ['yield', 'throughput']
    variables = [
        {'name': 'A', 'type': 'float', 'min': 0.05, 'max': 0.1},
        # Substrate_A_concentration,
        {'name': 'B', 'type': 'float', 'min': 2, 'max': 3.2},
        # Substrate_B_equivalent
        {'name': 'C', 'type': 'discrete', 'items': ['C1', 'C2']},
        # Substrate_C_type
        {'name': 'C_equiv', 'type': 'float', 'min': 0.5, 'max': 1.3},
        # Substrate_C_equivalent
        {'name': 'residence_time', 'type': 'float', 'min': 20, 'max': 1200},
        # Residence time (60 s --> 2 mL/min [2 ml reactor])
        {'name': 'eagle_percentage', 'type': 'float', 'min': 0, 'max': 100}
    ]
    reactor_volume = 5.0
    figure_name_objectives = 'figure_objectives.png'  # 'Pareto_front.png'
    figure_name_hypervolume = 'figure_hypervolume.png'
    total_number_of_runs = 26
    get_visualization(filename_json, variables, reactor_volume, figure_name_hypervolume, figure_name_objectives,
                      objectives, total_number_of_runs)