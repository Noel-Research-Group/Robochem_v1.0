""""
Diego Pintossi
Noël Research Group
Van 't Hoff Institute for Molecular Sciences (HIMS)
Universiteit van Amsterdam (UvA)

2021-09-01

Functions to analyze the signal from a phase sensor and identify the larger
droplets containing the reaction mixture.
"""

import pandas as pd
import scipy.signal
from Phase_sensors.Phase_sensor_data_export import export_droplets_data


def import_phase_sensor_data(filename):
    """ Import the phase sensor signal data from a CSV (exported pd.DataFrame)

    :param filename: string
        Name of the CSV file storing the data
    :return:
        pd.DataFrame containing the data
    """
    return pd.read_csv(filename)


def limited_import_phase_sensor_data(filename: object, sample_time: object = 60) -> object:
    """ Import the phase sensor signal data from a CSV (exported pd.DataFrame)

    :param filename: string
        Name of the CSV file storing the data
    :param sample_time: float
        Time interval of phase sensor data to be considered for import
    :return:
        pd.DataFrame containing the data
    """
    ps_data = pd.read_csv(filename)
    latest_data = ps_data[
        ps_data['Time [s]'] > ps_data.loc[
            len(ps_data.index) - 1, 'Time [s]'
        ] - sample_time
    ]
    latest_data.reset_index(drop=True, inplace=True)
    return latest_data


def signal_derivative(df, index):
    """ Function to calculate the derivative (1st order) based on the central
    difference scheme (except for the boundaries).

    :param df: Pandas.DataFrame
        DataFrame containing the data
    :param index: int
        Index of the time series point under consideration
    :return: float
        Derivative of the signal at the considered time
    """
    if index == 0:
        # forward difference scheme
        return (
                (df.loc[index + 1, 'Phase'] - df.loc[index, 'Phase'])
                / (df.loc[index + 1, 'Time [s]'] - df.loc[index, 'Time [s]'])
        )
    elif index == len(df.index) - 1:
        # backward difference scheme
        return (
                (df.loc[index, 'Phase'] - df.loc[index - 1, 'Phase'])
                / (df.loc[index, 'Time [s]'] - df.loc[index - 1, 'Time [s]'])
        )
    else:
        # central difference scheme
        return (
                (df.loc[index + 1, 'Phase'] - df.loc[index - 1, 'Phase'])
                / (df.loc[index + 1, 'Time [s]']
                   - df.loc[index - 1, 'Time [s]'])
        )


def droplet_start(df, index):
    """ Function to identify the start of a liquid droplet in the phase
    sensor time series.

    :param df: pandas.DataFrame
        DataFrame containing the data
    :param index: int
        Index of the time series point under consideration
    :return: bool
        Boolean value indicating if the point under consideration is the
        starting point for a droplet.
    """
    return True if signal_derivative(df, index) > 0 else False


def droplet_stop(df, index):
    """ Function to identify the end of a liquid droplet in the phase
    sensor time series.

    :param df: pandas.DataFrame
        DataFrame containing the data
    :param index: int
        Index of the time series point under consideration
    :return: bool
        Boolean value indicating if the point under consideration is the
        ending point for a droplet.
    """
    return True if signal_derivative(df, index) < 0 else False


def measure_droplets(data, filter_kernel=5,):
    """ Function to extract the size [s] of the droplet detected
    by the phase sensor.
    Also labeling droplets much larger than the carrier volume (assumed equal
    to the most frequent size detected) as reaction droplets.

    :param data: pandas.DataFrame
        pandas.DataFrame containing the phase sensor signal data
    :param filter_kernel: int
        Scalar describing the size of the median filter window
        NOTE: it has to be an odd number, e.g., 1-3-5-...
        (input for scipy.signal.medfilt)
    :return: pandas.DataFrame
        New dataframe with the analysed data
    """
    # Apply a median filter to the date to remove spikes
    data['Phase'] = scipy.signal.medfilt(data['Phase'], filter_kernel)
    # find droplets start and stop points
    data.insert(
        3, 'Start', [droplet_start(data, j) for j in range(len(data.index))]
    )
    data.insert(
        4, 'Stop', [droplet_stop(data, k) for k in range(len(data.index))]
    )
    data.insert(5, 'Start_time', data[:]['Time [s]'] * data[:]['Start'])
    data.insert(6, 'Stop_time', data[:]['Time [s]'] * data[:]['Stop'])

    # Calculate the sizes of the droplets
    data.insert(7, 'Drop_size [s]', '')
    droplets = []
    i = 0  # counter
    while i < len(data.index):
        if data.loc[i, 'Start']:  # find start event
            time_start = data.loc[i, 'Start_time']
            j = i
            while j < len(data.index):  # search for corresponding stop
                if data.loc[j, 'Stop']:
                    time_stop = data.loc[j, 'Stop_time']
                    drop_size = time_stop - time_start
                    droplets.append(drop_size)
                    data.at[j, 'Drop_size [s]'] = str(drop_size)
                    break
                j += 1
            i += 2  # derivative > 0 for two points in a row
        i += 1

    # Calculate the sizes of the gas bubbles
    data.insert(8, 'Bubble_size [s]', '')
    bubbles = []
    i = 0  # counter
    while i < len(data.index):
        if data.loc[i, 'Stop']:  # find stop event
            time_stop = data.loc[i, 'Stop_time']
            j = i
            while j < len(data.index):  # search for corresponding stop
                if data.loc[j, 'Start']:
                    time_start = data.loc[j, 'Start_time']
                    bubble_size = time_start - time_stop
                    bubbles.append(bubble_size)
                    data.at[j, 'Bubble_size [s]'] = str(bubble_size)
                    break
                j += 1
            i += 2  # derivative > 0 for two points in a row
        i += 1

    data = data.drop(['Start', 'Stop'], axis=1)  # remove boolean mask columns

    # store the values of the signal derivative in the DataFrame
    try:
        derivative = [
            signal_derivative(data, i) for i in range(len(data.index))
        ]
    except:
        pass
    data.insert(3, 'dPhase/dt', derivative)

    # Identify the reaction droplets
    droplet_identity = []
    for i in range(len(data.index)):
        # Look for detected droplets
        if data.loc[i, 'Drop_size [s]']:  # droplet is found
            d1 = float(data.loc[i, 'Drop_size [s]'])
            # Look for detected bubble preceding the droplet
            for j in range(i, 0, -1):
                if data.loc[j, 'Bubble_size [s]']:  # leading bubble found
                    b1 = float(data.loc[j, 'Bubble_size [s]'])
                    break
                else:  # no leading bubble found
                    b1 = 0
            # Search for detected bubble following the droplet
            for k in range(i, len(data.index)):
                if data.loc[k, 'Bubble_size [s]']:  # trailing bubble found
                    b2 = float(data.loc[k, 'Bubble_size [s]'])
                    break
                else:  # no trailing bubble found
                    b2 = 0
            # Droplet found + leading and trailing bubbles
            # Filtering small size bubbles is done at line 175
            if b1 > 0 and b2 > 0:
                droplet_identity.append(True)
            else:
                droplet_identity.append(False)
        else:
            droplet_identity.append(False)
    data.insert(8, 'Reaction drop', droplet_identity)
    return data


async def identify_reaction_mix(phase_data, droplets_data, sample_time=500):
    """ Script to identify reaction slug volumes in a chunk of phase sensor data

    :param phase_data: str
        CSV file containing the phase sensor data
    :param droplets_data: set
        a set of the unique times of each detected droplet
    :param sample_time: float
        How far back [s] to go in retrieving data
        IMPORTANT: this interval should be large enough to let the system
        see at least two gas bubbles + one reaction volume
    :return: bool
        True if reaction volume is detected
    """
    ps_data = limited_import_phase_sensor_data(
        phase_data,
        sample_time=sample_time
    )

    try:
        # create DataFrame with analyzed phase sensor data
        # TODO kernel size is hard-coded for now
        limited_df = measure_droplets(ps_data, filter_kernel=7)

        if limited_df['Reaction drop'].any():
            time_df = limited_df[:]['Time [s]'] * limited_df[:]['Reaction drop']
            time_df_unique = set(time_df)  # remove duplicates (empty lines)
            time_df_unique.remove(0)  # remove only empty line left
            for item in time_df_unique:
                droplets_log = pd.read_csv(droplets_data)
                # Check if detected droplet is new
                if float(item) not in set(droplets_log['Time [s]']):
                    await export_droplets_data(droplets_data, item)
                    return True
                else:
                    return False
        else:
            return False
    except Exception as ex:
        # TODO log this instead of printing to console
        print(ex)
        print('identify_reaction_mix() ran into the exception above.')
        return False


if __name__ == "__main__":
    None