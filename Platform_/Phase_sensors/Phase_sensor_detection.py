import asyncio
import pandas as pd

from Phase_sensors.Droplet_identification import identify_reaction_mix
import phase_sensor_CSV_naming


def ps_data_filename(phase_sensor):
    """Function to retrieve the name of the CSV file storing the filenames
    for the phase sensor data logs for each sensor.

    Note: this is different from generating again the filename, since that would
    create a new (different) timestamp.

    :param phase_sensor: string
        Name of the phase sensor (e.g. 'PS1' for Phase Sensor 1)
    :return: string
        Filename of the phase sensor data log
    """
    filenames_ps = {
        'PS1': pd.read_csv(
            phase_sensor_CSV_naming.get_CSV_with_names_ps(),
            index_col=0
        )['0'][0],
        'PS2': pd.read_csv(
            phase_sensor_CSV_naming.get_CSV_with_names_ps(),
            index_col=0
        )['0'][1],
        'PS3': pd.read_csv(
            phase_sensor_CSV_naming.get_CSV_with_names_ps(),
            index_col=0
        )['0'][2],
        'PS4': pd.read_csv(
            phase_sensor_CSV_naming.get_CSV_with_names_ps(),
            index_col=0
        )['0'][3],
        'PS5': pd.read_csv(
            phase_sensor_CSV_naming.get_CSV_with_names_ps(),
            index_col=0
        )['0'][4],
        'PS6': pd.read_csv(
            phase_sensor_CSV_naming.get_CSV_with_names_ps(),
            index_col=0
        )['0'][5],
        'PS7': pd.read_csv(
            phase_sensor_CSV_naming.get_CSV_with_names_ps(),
            index_col=0
        )['0'][6],
    }
    return filenames_ps[phase_sensor]


def droplet_data_filename(phase_sensor):
    """Function to retrieve the name of the CSV file storing the filenames
    for the droplet logs for each phase sensor.

    Note: this is different from generating again the filename, since that would
    create a new (different) timestamp.

    :param phase_sensor: string
        Name of the phase sensor (e.g. 'PS1' for Phase Sensor 1)
    :return: string
        Filename of the droplet log
    """
    filenames_droplets = {
        'PS1': pd.read_csv(
            phase_sensor_CSV_naming.get_CSV_with_names_droplets(),
            index_col=0
        )['0'][0],
        'PS2': pd.read_csv(
            phase_sensor_CSV_naming.get_CSV_with_names_droplets(),
            index_col=0
        )['0'][1],
        'PS3': pd.read_csv(
            phase_sensor_CSV_naming.get_CSV_with_names_droplets(),
            index_col=0
        )['0'][2],
        'PS4': pd.read_csv(
            phase_sensor_CSV_naming.get_CSV_with_names_droplets(),
            index_col=0
        )['0'][3],
        'PS5': pd.read_csv(
            phase_sensor_CSV_naming.get_CSV_with_names_droplets(),
            index_col=0
        )['0'][4],
        'PS6': pd.read_csv(
            phase_sensor_CSV_naming.get_CSV_with_names_droplets(),
            index_col=0
        )['0'][5],
        'PS7': pd.read_csv(
            phase_sensor_CSV_naming.get_CSV_with_names_droplets(),
            index_col=0
        )['0'][6],
    }
    return filenames_droplets[phase_sensor]


async def droplet_detection_loop(phase_sensor,
                                 analysed_interval=300,
                                 frequency=1):
    """ Loop to analyze phase sensor data continuously.

    This function is used to detect if a droplet has passed the phase
    sensor. The frequency determines how often this is being checked.
    When a droplet has been found, the loop is broken and True is
    returned.

    :param phase_sensor: string
        The name of the phase sensor (e.g., 'PS1' for Phase Sensor 1).
    :param analysed_interval: float
        How far back in time [s] the data analysis should cover
        (e.g., if 60, then the last 60 seconds of data will be analyzed)
    :param frequency: float
        Time interval [s] between successive analyses
    :result: boolean
        Returns True when a droplet has been found.
    """
    print(f'Droplet detection loop active at {phase_sensor}.')
    # loop to analyse the data continuously
    while True:
        # [!!!] this assumes that a separate loop exports to the CSV
        await asyncio.sleep(frequency)
        print(f'Detection loop ({phase_sensor}) still running!')
        detected = await identify_reaction_mix(
            ps_data_filename(phase_sensor),
            droplet_data_filename(phase_sensor),
            sample_time=analysed_interval
        )
        if detected:  # this can be used as a trigger event (breaks loop)
            print(f'Found a droplet! {ps_data_filename(phase_sensor)[-7:-4]}')
            # return True
            break
    return True


if __name__ == '__main__':

    FILENAME = '/Phase_sensor_DATA/2022-02-09/2022-02-09_T1644_PS6.csv'

    asyncio.run(
        droplet_detection_loop(
            phase_sensor='PS6',
            analysed_interval=180,
            frequency=2,
        )
    )