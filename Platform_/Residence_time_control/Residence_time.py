"""
Diego Pintossi\n
Flow Chemistry Group\n
Van 't Hoff Institute for Molecular Sciences (HIMS)\n
Universiteit van Amsterdam (UvA)\n

2021-10-15\n

Function to convert the residence time (output of the BO process) into its
corresponding flow rate.

"""


def find_flow_rate(residence_time, reactor_volume):
    """Function to calculate the flow rate to achieve the desired residence_time
    [s], based on the reactor_volume [mL]

    :param residence_time: float
        Residence time for the reaction [s]
    :param reactor_volume: float
        Internal volume of the reactor [mL]
    :return: float
        Flow rate [mL/min] corresponding to the desired residence time
    """
    return 60 * reactor_volume / residence_time


if __name__ == '__main__':
    vol = 1.5
    for _ in range(30, 630, 30):
        print(f'Volume: {vol} mL.')
        print(f'Residence time: {_} s.')
        print(f'Flow rate: {find_flow_rate(_, vol)} mL/min\n')
