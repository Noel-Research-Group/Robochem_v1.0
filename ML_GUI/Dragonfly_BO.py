""" Bayesian Optimization from dragonfly.

In this files the functions for running single- and multi-objective optimization using Bayesian Optimization are found.
The package used is provided by Dragonfly. Since the folder ML-GUI runs with python 32-bit and Platform_ with python
64-bit when the bayesian optimization needs to run the platform, it does it

note: ignore Fortran warning

Author: Pauline Tenblad
"""

import numpy as np
#----------------------------------------------------------------------------------------------------------------------#
# This is Grace's code to fix the numpy depreciation, Thanks Grace!
# the following code is a necessary but ugly fix for a numpy depreciation - I'm still hoping Dragonfly will release an update
# From numpy 1.20.0 certain numpy names for python types were depreciated
# this code basically reassigns that name to the object
# this is not best practice - keep checking for Dragonfly updates
# np.object = object
# you might need these other assignments later but I haven't tested them yet
# np.bool = bool
# np.int = int
# np.float = float
# np.complex = complex
# np.str = str
# np.long = int
# np.unicode = str
#-----------------------------------------------------------------------------------------------------------------------


from Visualization import get_visualization
from argparse import Namespace
from dragonfly import load_config
from dragonfly.exd.experiment_caller import CPFunctionCaller, CPMultiFunctionCaller
from dragonfly.opt.gp_bandit import CPGPBandit
from dragonfly.opt.multiobjective_gp_bandit import CPMultiObjectiveGPBandit
from dragonfly.exd.worker_manager import SyntheticWorkerManager

# Utilities
import os
import time
import pickle
import json
from ast import literal_eval
import subprocess


# Define constants
FILENAME_INPUT_PICKLE = os.path.join('..','input.pickle')  # Same location for frontend and backend. ('..' to move up a folder) #TODO> maybe change here?
FILENAME_OUTPUT_PICKLE = os.path.join('..','output.pickle')  # Same location for frontend and backend. ('..' to move up a folder)
FILENAME_OUTPUT_CSV = os.path.join('..','all_output.csv')  # Same location for frontend and backend. ('..' to move up a folder)

FIGURE_NAME_OBJECTIVES = 'figure_objectives.png'
FIGURE_NAME_HYPERVOLUME = 'figure_hypervolume.png'

TIME_SLEEP = 0.5  # [s] The time to sleep inbetween updating the frontend.

def get_conda_env_path(env_name):
    '''for some reason conda run does not work in subprocess so we try to go directly and
    use the python executable for the 32 bit env'''
    cmd = 'conda info --envs'
    result =subprocess.run(cmd, shell = True, text = True,
                           stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    # get the output lines:
    lines = result.stdout.splitlines()

    # get the environment path:
    for line in lines:
        if env_name in line:
            # the path is the end of the line
            return line.split()[-1]
    return None

def get_python_executable(env_name):
    env_path = get_conda_env_path(env_name)
    if not env_path:
        return None
    # Construct path to Python executable
    python_path = subprocess.os.path.join(env_path, 'bin',
                                          'python')  # UNIX-like systems
    if subprocess.sys.platform == 'win32':
        python_path = subprocess.os.path.join(env_path,
                                              'python.exe')  # Windows

    return python_path


def run_platform(index, x, objectives, variables_):
    # """ Function that runs the platform and returns the yield.
    #
    # :param index: int
    #     index to keep track of the current run.
    # :param x: list
    #     list with values for each parameter in the parameter space.
    # :param objectives: str
    #     'single', 'multi' for single objective and multi objective optimization respectively.
    # :param variables_: list
    #     List of the defined variable space.
    # :return: returns the y-value, yield for single objective optimization
    #     or yield and selectivity for multi objective optimization.
    # """
    # STEP 1: Add the input to a csv file
    with open(FILENAME_INPUT_PICKLE, 'wb') as filepointer:
        pickle.dump([index, x, objectives, variables_], filepointer)
    print([index, x, objectives, variables_] )
    # STEP 2: Activate the platform
    # older depreciated os.popen commands commented out
    # os.popen('..\\Platform_\\venv\\Scripts\\activate && python ..\\Platform_\\run_test.py', 'w')
    # os.popen('..\\Platform_\\venv\\Scripts\\activate && python ..\\Platform_\\run_platform.py', 'w')
    # using 32-bit conda environment
    # run optimization as a separate thread
    #find executable:
    executable = get_python_executable('robochem_platform_32bit')
    # setting up the command 'conda run -n robochem_crossplatform python ..\\ML_GUI\\run_optimization_from_gui.py'
    # cmd_args = ['conda', 'run', '-n', 'robochem_platform_32bit', 'python', '..\\Platform_\\run_platform.py']
    cmd_args = [executable, '..\\Platform_\\run_platform.py']
    # sending the command to a new thread
    # NOTE: 1. despite online advice shell must be set to True for the command to find the python file
    # NOTE: 2. the stdin and stdout must be linked to the subprocess.PIPE variable for the command to be sent
    proc = subprocess.Popen(cmd_args,
                                # stdin=subprocess.PIPE,
                                # stdout=subprocess.PIPE,
                                shell=True)


    # STEP 3: Wait for the platform to generate the result
    # This line of code is constantly being read. The input pickle (x value to platform) contains the new index.
    # While the platform is running the output pickle (y from platform to BO) has not yet been updated, thus it has the
    # old index value. Thus we are waiting for the indexes to match, first then can we return the y value!
    while True:
        time.sleep(TIME_SLEEP)
        if os.path.exists(FILENAME_OUTPUT_PICKLE):
            with open(FILENAME_OUTPUT_PICKLE, 'rb') as filepointer:
                [index_, x_, y_, timestamp] = pickle.load(filepointer)
                if index_ == index:
                    return y_

def transform_variables(variables):
    '''We figured out that the new streamlit passes the variables in the wrong way to bo. here's a little function that should fix it'''
    transformed = []
    skip_next = False

    for i in range(len(variables)):
        if skip_next:
            skip_next = False
            continue

        var = variables[i]

        # Check if the next variable is a 'conc' pair
        if i + 1 <len(variables) and var['name'] in variables[i +1]['name'] and ('conc' in variables[i + 1]['name']
            or 'equiv' in variables[i + 1]['name'] or 'loading' in variables[i + 1]['name']):
            if var['type'] == "discrete" and len(var['items']) == 1:
                # Transform the variable
                new_var = {
                    "name": var['items'][0],
                    "type": "float",
                    "min": variables[i + 1]['min'],
                    "max": variables[i + 1]['max']
                }
                transformed.append(new_var)
                skip_next = True  # Skip the next variable as it's the conc pair
            else:
                # Add both pairs as they are
                transformed.append(var)
                transformed.append(variables[i + 1])
                skip_next = True
        else:
            # Add the variable as it is
            transformed.append(var)

    return transformed


def format_input_with_variable_names(transformed_variables, input_values):
    '''and of course the translation back to an input that the platform can understand'''
    formatted_input = []
    input_idx = 0

    for var in transformed_variables:
        # Skip the discrete variable name in transformed_variables
        if var['type'] == 'discrete':
            continue

        # Check if the next value in input_values is a string (i.e., a discrete variable name)
        # If it is, add both the name and the value as they are
        if isinstance(input_values[input_idx], str):
            formatted_input.append(input_values[input_idx])
            input_idx += 1
            formatted_input.append(input_values[input_idx])
        else:
            # For float variables, prepend the variable name
            formatted_input.append(var['name'])
            formatted_input.append(input_values[input_idx])

        input_idx += 1

        # Handling the last two values
        if input_idx >= len(input_values) - 2:
            return formatted_input + input_values[input_idx:]

    return formatted_input

def format_previous_with_fixed_vars(transformed_vars, output_list):
    '''specifically used when the run from previous is used. it transform platform
    input to BO input'''


    discrete_vars = [vals['items'] for vals in transformed_vars if vals['type'] == 'discrete']

    cleaned_output = [item for item in output_list if not isinstance(item,str) or item in discrete_vars]
    return cleaned_output

def dragonfly_bo(reactor_volume, variables_, num_init_, num_total_, objectives_, dict_filename_, previous_runs_=False,
                 ):
    """ Bayesian optimization for single and multi objective optimization.

    Default is to run single objective optimization. To run multi objective optimizations change objectives_ to 'multi'
    and add the number of objectives to num_objectives_.
    To run initialization phase using results from previous runs, change previous_runs to 'True' and add the filename of
    the dict from that run.

    :param reactor_volume: float
        the reactor volume
    :param variables_: list
        list of dictionary with the parameters spanning the experimental domain
    :param num_init_: int
        number of initial experiments
    :param num_total_: int
        total number of experiments, initial experiments are included
    :param objectives_: list
        list of the objective functions to optimize over. If only one object it is 'single' objective optimization,
         if more than one object in the list it is 'multi' objective optimization.
    :param previous_runs_: boolean
        True if previous runs should be included, False otherwise
    :param dict_filename_: str
        json file containing a dictionary with all previous runs that should be included
    :return:
    """

    fixed_vars = transform_variables(variables_)

    # Create domain from variables
    config_params = {'domain': fixed_vars}
    config = load_config(config_params)

    # User settings
    batch_size = 1  # number of new experiments you want to query at each iteration

    if len(objectives_) == 1:  # Single objective optimization
        # Specify algorithm settings
        options = Namespace(
            build_new_model_every=batch_size,  # set to batch size
            init_capital=num_init_ - 1,  # number of initialization experiments
            # (-1 is included since Dragonfly generates n+1 experiments)
            gpb_hp_tune_criterion='ml-post_sampling',  # Criterion for tuning GP hyper-parameters.
            # Options: 'ml-post_sampling' (algorithm default), 'ml', 'post_sampling'.
        )

        # Create optimizer object
        func_caller = CPFunctionCaller(None, config.domain, domain_orderings=config.domain_orderings)
        opt = CPGPBandit(func_caller, 'default', ask_tell_mode=True, options=options)  # opt is the optimizer object

    if len(objectives_) > 1:  # Multi objective optimization
        # Specify algorithm settings
        options = Namespace(
            build_new_model_every=batch_size,  # set to batch size
            init_capital=num_init_ - 1,  # number of initialization experiments
            # (-1 is included since Dragonfly generates n+1 experiments)
            gpb_hp_tune_criterion='ml-post_sampling',  # Criterion for tuning GP hyper-parameters.
            # Options: 'ml-post_sampling' (algorithm default), 'ml', 'post_sampling'.
            moors_scalarisation='linear',  # Scalarization approach for multi-objective opt. 'linear' or 'tchebychev'
        )

        # Create optimizer object
        func_caller = CPMultiFunctionCaller(None, config.domain, domain_orderings=config.domain_orderings)
        func_caller.num_funcs = len(objectives_)  # must specify how many functions are being optimized

        wm = SyntheticWorkerManager(1)
        opt = CPMultiObjectiveGPBandit(func_caller, wm, options=options)
        opt.ask_tell_mode = True
        opt.worker_manager = None
        opt._set_up()
    # from gui previous_runs_ is stored as 'No' which you can imagine python has trouble
    # interpreting as FALSE and tries to start up previous runs where not needed.
    # Therefore let me add a fix for that xoxo-ES
    if previous_runs_ == 'No':
        previous_runs_ = False # NOT ROBUST AT ALL BUT we gotta work with what we got

    # ---------------------------- BUILD FROM RANDOM GENERATED INITIALIZATION POINTS -----------------------------------
    if not previous_runs_:
        opt.initialise()  # this generates initialization points
        init_expts = opt.ask(num_init_)  # get all initialization points

        # Run each experiment
        expts_dict = {}  # Create an empty dictionary to store each experiment
        index = 1
        for x in init_expts:  # x is a list of
            x_transformed = format_input_with_variable_names(fixed_vars, x)
            y = run_platform(index, x_transformed, objectives_, variables_)  # simulate
            # reaction

            expts_dict[repr(x_transformed)] = y # list are an unhashable type
            with open(FILENAME_OUTPUT_PICKLE, 'rb') as filepointer:  # Read the output pickle to also have the timestamp
                [index_, x_, y_, timestamp] = pickle.load(filepointer)

            expts_dict[repr(x_transformed)] = [y, timestamp]  # list are an unhashable type
            with open(dict_filename_, 'w') as filepointer:
                json.dump(expts_dict, filepointer, indent=True)
            index += 1
            opt.tell([(x, y)])  # return result to algorithm
            opt.step_idx += 1  # increment experiment number
            print("expt #:", opt.step_idx, ", x:", x_transformed, ", y:", y, ", timestamp:", timestamp)

            # When the json-file has been updated, the scatter plot of the objectives and the plots for hypervolume
            # has to be updated aswell.
            get_visualization(dict_filename_, variables_, reactor_volume, FIGURE_NAME_HYPERVOLUME,
                              FIGURE_NAME_OBJECTIVES, objectives_, num_total_)

    # ----------------------------- BUILD FROM PREVIOUS RUNS (for instance for interrupted runs) -----------------------
    if previous_runs_:
        opt.initialise()  # this generates initialization points
        init_expts = opt.ask(num_init_)  # get all initialization points

        # Note: To provide your own initialization data to the algorithm,
        # execute the above 2 lines (which clear the initial experiments generated by the algorithm)
        # and return as many data points as you want in the for loop below.
        with open(dict_filename_, 'r') as filepointer:
            expts_dict = json.load(filepointer)

        index = 1
        for x, [y, timestamp] in expts_dict.items():
            x_cleaned = format_previous_with_fixed_vars(fixed_vars, literal_eval(x))
            index += 1
            opt.tell([(x_cleaned, y)])  # return result to algorithm
            opt.step_idx += 1  # increment experiment number
            print("expt #:", opt.step_idx, ", x:", x, ", y:", y, ", timestamp:", timestamp)

    # Update model using results
    opt._build_new_model()  # key line! update model using prior results
    opt._set_next_gp()  # key line! set next GP

    # While experiment budget has not been exceeded
    while opt.step_idx < num_total_:

        # Get a new batch of experiments
        batch = []
        for i in range(batch_size):
            x = opt.ask()
            batch.append(x)

        # Run each experiment
        for x in batch:
            x_transformed = format_input_with_variable_names(fixed_vars, x)
            print(x_transformed)
            y = run_platform(index, x_transformed, objectives_, variables_)  # simulate reaction
            with open(FILENAME_OUTPUT_PICKLE, 'rb') as filepointer:  # Read the output pickle to also have the timestamp
                [index_, x_, y_, timestamp] = pickle.load(filepointer)

            expts_dict[repr(x_transformed)] = [y, timestamp]  # list are an unhashable type
            with open(dict_filename_, 'w') as filepointer:
                json.dump(expts_dict, filepointer, indent=True)
            index += 1
            opt.tell([(x, y)])
            opt.step_idx += 1
            print("expt #:", opt.step_idx, ", x:", x_transformed, ", y:", y, ", timestamp:", timestamp)

            # When the json-file has been updated, the scatter plot of the objectives and the plots for hypervolume
            # has to be updated aswell.
            get_visualization(dict_filename_, variables_, reactor_volume, FIGURE_NAME_HYPERVOLUME,
                              FIGURE_NAME_OBJECTIVES, objectives_, num_total)


        # Update model
        opt._build_new_model()
        opt._set_next_gp()

    # run the EagleReactor Script
    # find the python executable:
    executable = get_python_executable('robochem_platform_32bit')
    # os.popen('..\\Platform_\\venv\\Scripts\\activate && python ..\\Platform_\\Eagle_Reactor\\Eagle_control.py', 'w')
    # using the 32-bit conda environment
    # setting up the command 'conda run -n robochem_crossplatform python ..\\ML_GUI\\run_optimization_from_gui.py'
    # cmd_args = ['conda', 'run', '-n', 'robochem_platform_32bit', 'python', '..\\Platform_\\Eagle_Reactor\\Eagle_control.py']
    cmd_args = [executable,'..\\Platform_\\Eagle_Reactor\\Eagle_control.py']
    # sending the command to a new thread
    # NOTE: 1. despite online advice shell must be set to True for the command to find the python file
    # NOTE: 2. the stdin and stdout must be linked to the subprocess.PIPE variable for the command to be sent
    proc = subprocess.Popen(cmd_args,
                            # stdin=subprocess.PIPE,
                            # stdout=subprocess.PIPE,
                            shell=True)


if __name__ == '__main__':
    variables = [
        {'name': 'A', 'type': 'discrete', 'items': ['A1',
                                                    'A2']},
        {'name': 'A_conc', 'type': 'float', 'min': 0.05, 'max': 0.08},
        # Substrate_A_concentration,
        {'name': 'B', 'type': 'float', 'min': 2, 'max': 3.2},
        # tetrahydrofuran_equivalent
        {'name': 'C', 'type': 'discrete', 'items': ['C1', 'C2']},
        {'name': 'C_equiv', 'type': 'float', 'min': 0.5, 'max': 1.3},
        # Catalyst loading
        {'name': 'residence_time', 'type': 'float', 'min': 240, 'max': 1200},
        # Residence time (60 s --> 2 mL/min [2 ml reactor])
        {'name': 'eagle_percentage', 'type': 'float', 'min': 0, 'max': 100}
    ]

    # User settings
    num_init = 12  # number of initialization experiments
    num_total = 30  # number of total experiments to perform

    dragonfly_bo(0.63, variables, num_init, num_total, objectives_=['yield',
                                                                    'throughput'],
                 dict_filename_='../AS_example.json',
                 previous_runs_=False,)
