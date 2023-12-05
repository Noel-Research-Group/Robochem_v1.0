"""A set of Calculator Functions to check whether the Substrates concentrations and equivalents of
given reagent conditions are possible.

This is used when running the platform alone and without the GUI

Aidan Slattery
"""

import numpy as np
import pandas as pd
from phase_sensor_CSV_naming import get_your_abs_project_path


def sample_check():
    """
    Function to check that the stock solution concentrations and amounts are sufficient for the optimization

    :raise Exception
        Custom exception if stock solution concentrations and volumes do not allow optimization
    :return list
        maximum possible volumes for stock solution vials
    :return list
        minimum possible volumes for stock solution vials
    """
    slug_size = 0.65
    stock_conc = [2.0, 12.3, 0.015] #M stock solutions. Sub A, Sub B, cat
    max_reaction = [0.2, 18, 0.03]#Conc (Sub A) and eq. (rest) for a maxed out reaction
    min_reaction = [0.05, 1, 0.01]

    max_volumes = []
    min_volumes = []
    for _ in range(len(stock_conc)):
        if _ == 0:
            max_vol = round((slug_size * max_reaction[0]) / stock_conc[0], 4)
            max_volumes.append(max_vol)
        else:
            vol = round((slug_size*(max_reaction[0]*max_reaction[_])) / (stock_conc[_]), 4)
            max_volumes.append(vol)
            max_vol += vol

    # In the maximum case for reagent, solvent is minimized
    max_reagent_volume = sum(max_volumes)
    min_solvent_volume = slug_size - max_reagent_volume
    max_volumes.append(round((min_solvent_volume), 4))
    print(f'\nmax reagent volume: {max_reagent_volume}')
    # In the minimum case for reagent, solvent is maximized
    min_reagent_volume = sum(min_volumes)
    max_solvent_volume = slug_size - min_reagent_volume
    min_volumes.append(round((max_solvent_volume), 4))

    if max_reagent_volume >= slug_size:
        raise Exception(f'Error: This concentration/equivalents combination is not ' \
              f'possible needed slugsize: {max_reagent_volume} ml'
              f'\nTry reducing the max equivalents or increasing the '
                        f'concentration\n')

    return max_volumes, min_volumes


def volume_check():
    """function to check that the minimum and maximum volumes
    are enough to test the maximum numbers of runs.
    Prints a response to the command line"""
    number_runs = 13
    max_volumes, min_volumes = sample_check()
    print(f'\nmax case: {max_volumes}   min case: {min_volumes}\n')
    volumes_needed = [volume * number_runs for volume in max_volumes]
    solvent_needed = min_volumes[-1] * number_runs

    print(f'Volumes Needed of the indicated stock solutions:\n'
          f'Sub_A: {round(volumes_needed[0], 2)} ml    '
          f'Sub_B: {round(volumes_needed[1], 2)} ml    '
          f'cat: {round(volumes_needed[2], 2)} ml    '
          f'Solvent: {round(solvent_needed, 2)} ml')

def max_throughput():
    """Function to print out a maximum throughput"""
    # mg/hr
    reactor_volume = 5 #ml
    reaction_yield = 1 #100%
    min_residence_s = 120 #s
    min_residence_hr = min_residence_s / (60 * 60)
    max_flow_rate_hr = reactor_volume/(min_residence_hr) #ml/hr
    concentration = 0.115 #mmol/ml
    throughput = concentration * max_flow_rate_hr #mmol/hr
    Mw = 200 #mg/mmol
    throughput_mg = Mw * throughput
    print(f'\nMax throughput: {throughput_mg} mg/hr')

def get_price():
    """
    Function to obtain the price of each component

    :return: dictionary of price
    """
    price_dict = {}

    filepath = '/Liquid_Handler/20230224_CF3_caffeine_ZWA-051.xlsx'
    sample_data = pd.read_excel(
        get_your_abs_project_path()
        + filepath,
        engine='openpyxl',
        keep_default_na=False
    )
    price_data = sample_data.iloc[27:38, 11:21]

    for i in range(price_data.shape[0]):
        for j in range(int(price_data.shape[1] / 2)):
            #  remove the empty value of sample name
            if price_data.values[i][2 * j] != 0 and price_data.values[i][2 * j] != '':
                compound_name = price_data.values[i][2 * j]
                price_dict[compound_name] = price_data.values[i][2 * j + 1]
            else:
                pass
    # print(price_dict)
    return price_dict


def calculate_objective_outputs(chemical_space, residence_time, reactor_volume, measured_exp_yield,
                                prices=None):
    """Prototype function for testing cost objectives"""
    limiting_reagent_mmol = chemical_space[1] * reactor_volume # continuous parameters
    mmol_generated = (limiting_reagent_mmol * (measured_exp_yield / 100))
    throughput = (mmol_generated / residence_time) * \
                 60 * 60  # mmol/s -> mmol/hr
    cost = 0
    sample_count = 0
    if prices != None:
        for condition in chemical_space:
            if type(condition) == str:
                sample_count += 1

        for i in range(sample_count):
            if mmol_generated == 0:
                cost = -100000
            else:
                if i == 0:
                    cost = -(limiting_reagent_mmol * prices[str(chemical_space[i])] /
                             mmol_generated)
                else:
                    # TODO: add the calculation of cost for different catalysts
                    cost_item = -(limiting_reagent_mmol * chemical_space[2 * i + 1] *
                                  prices[str(chemical_space[2 * i])] / mmol_generated)
                    cost += cost_item
    return throughput, cost


if __name__ == '__main__':
    # run the sample check
    print(sample_check())

