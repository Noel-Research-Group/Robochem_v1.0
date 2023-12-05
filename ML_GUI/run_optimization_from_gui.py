"""
PT,

Script to run optimization from the GUI!
"""

from Dragonfly_BO import dragonfly_bo
import json

if __name__ == '__main__':
    # Serializing json
    with open('../experimental_setup.json', 'r') as infile:
        experimental_setup = json.load(infile)
    print(experimental_setup)

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