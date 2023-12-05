"""Script to run the RoboChem platform

D.Pintossi, Aidan Slattery
2021-12-09

[add description]

"""
import pickle
from platform_class import Platform
from List_connected_devices import find_port
from experiment_execution import *
from Liquid_Handler.Sample_info import SampleInfo
from NMR_control_loop.NMR_processing import *
from Pumps_Valves_PS_MFC_LiquidHandler.Pumps_Valves_PS_MFC_LiquidHandler import SamplePreparation
from Syringe_pumps_and_valves_ensemble.Single_pump_and_valve_ensemble import SinglePumpValveEnsemble
from Liquid_Handler import *
from ultrasonic_detector.ultrasonic_pump_detection import UltrasonicDetector
from Eagle_Reactor.Eagle_control import EagleReactor
from variable_space import create_variable_space
from ast import literal_eval
# ------------------------------------------------------------------------------
# 1. Initialize the platform (connect to instrument, fill syringes)
# Parameters

REACTOR_VOLUME = 4.0

# Connect to devices
# [!] PS4-PS6 require manual setup of the COM port name
RoboChem = Platform(
    syringe_pump_a={
        'port': find_port('Syringe_pump_A'),
        'baudrate': 38400,
        'name': 'syringe_pump_a'
    },
    syringe_pump_b={
        'port': find_port('Syringe_pump_B'),
        'baudrate': 38400,
        'name': 'syringe_pump_b'
    },
    syringe_pump_c={
        'port': find_port('Syringe_pump_C'),
        'baudrate': 38400,
        'name': 'syringe_pump_c'
    },
    switch_valves={
        'port': find_port('Switch_valves'),
        'name': 'switch_valves',
        'pins': [8, 7, 4, 2],
        'valve types': ['3-way', '4-way', '3-way', '4-way']
    },
    mfc={'port': find_port('MFC')},
)

# Retrieve information on the vials loaded in the liquid handler
sample_information = SampleInfo(
    "C:\\Users\\Platform\\Platform_Data\\AS\\AS001\\AS001_LH_vial_positions.xlsx"
)
sample_information.get_sample_name()
sample_information.get_sample_info()
sample_information.initial_sample_info()
sample_information.get_sample_bottles_number()

liquid_handling = SamplePreparation(RoboChem)
pump_C = SinglePumpValveEnsemble(RoboChem)
detectors = UltrasonicDetector()

# Set MFC to MAX flow rate (in conjunction with home-made ~1 atm BPR)
asyncio.run(
    liquid_handling.pumps_valves.MFC.define_setpoint(0.0)
)

# Set 4-way valve next to the NMR to send solvent to waste
asyncio.run(
    RoboChem.switch_valves.valve_4_OFF_or_C_3()
)


# Fill syringes (A+B, C) with solvent
async def fill_up_syringes():
    """Coroutine to fill up all syringes concurrently.
    """
    # vol_a = asyncio.run(detectors.get_volume(pump='A'))
    # vol_b = asyncio.run(detectors.get_volume(pump='B'))
    # vol_c = asyncio.run(detectors.get_volume(pump='C'))
    # or
    vol_a, vol_b, vol_c = await asyncio.gather(
        detectors.get_volume(pump='A'),
        detectors.get_volume(pump='B'),
        detectors.get_volume(pump='C')
    )
    # vol_a, vol_b = await asyncio.gather(
    #     detectors.get_volume(pump='A'),
    #     detectors.get_volume(pump='B')
    #     # detectors.get_volume(pump='C')
    # )
    print(f'\nPump A: {vol_a} ul  Pump B: {vol_b} ul  Pump C: {vol_c} ul')
    await asyncio.gather(
        liquid_handling.pumps_valves.PumpsValvesEnsemble.ensemble_start_up_no_fill(
            vol_start_a=vol_a,  # volumes in microliters!
            vol_start_b=vol_b,
            diameter_a=14.47,  # SGE syringe (gas-tight) 10 mL
            diameter_b=14.47
        ),
        pump_C.pump_start_up_no_fill(
            vol_start_c=vol_c,
            diameter_c=23.03  # for 25 mL gas-tight syringe
        )
    )

# asyncio.run(
#     fill_up_syringes()
# )

# Initialize NMR file
# nmr_processing.initialize_nmr_csv()

# ------------------------------------------------------------------------------
# 2a. Define parameters space for the experiment
#    NOTE1: the sample information in the Excel is processed by LH (separately)
#    NOTE2: the reaction parameters are specific to each optimization campaign

exp_parameters = [
    'A',  # ID of limiting reagent
    0.150,  # conc. of limiting reagent
    'B',  # ID of reagent B
    9.5,  # equiv. of reagent B wrt A
    'C',  # ID of reagent C
    0.02,  # equiv. of reagent C wrt A
    240,  # residence time (s)
    50  # % power of reactor
]

# ------------------------------------------------------------------------------
# 2b. Wrap the experiment function in a format compatible with BO
def run_platform(X):
    """Function to be fed to the BO. Accepting a single vector as input,
    returning a single number as output.

    :param X: list
        List containing the sample concentration parameters and the residence
        time.
    :return: float
        The calculated yield from the executed reaction.
    """
    with open('../input.pickle', 'rb') as filepointer:
        [index_, x_, objectives_, variables_] = pickle.load(filepointer)
    asyncio.run(fill_up_syringes())
    asyncio.run(pump_C.refill_syringe())
    Eagle = EagleReactor()
    print(X)
    # print(variables_)
    residence_time, eagle_percentage, chemical_space = create_variable_space(X,
                                                                          variables_)
    print(chemical_space)
    # eagle_percentage = Eagle.convert_intensity(eagle_wattage)
    Eagle.light_on_with_level(level=eagle_percentage)


    # Run experiment and calculate yield (Basic functionality)
    conditions = literal_eval(repr(X))
    measured_exp_yield = asyncio.run(
        single_automated_experiment(
            RoboChem,
            liquid_handling,
            pump_C,
            chemical_space,
            sample_information.prepare_sample_info(chemical_space),
            residence_time,  # residence time (always placed last in the list)
            REACTOR_VOLUME  # global variable from the script
        )
    )

    RoboChem.switch_valves.close()
    RoboChem.mfc.close()
    detectors.close()

    print(f'The measured yield is: {measured_exp_yield}')


# ------------------------------------------------------------------------------
# 3. Execute the experiment
if __name__ == "__main__":
    # Execute experiment
    run_platform(exp_parameters)