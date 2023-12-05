from datetime import datetime
import pandas as pd
import time


def initialize_phase_sensor_csv(name):
    """ Function to create an empty pandas.DataFrame and export it to CSV.
    This file will be used to log data from a phase sensor.

    :param name: string
        Filename for the CSV
    """
    phase_data_log = pd.DataFrame(columns=['Time [s]',
                                           'Time',
                                           'Phase'])
    phase_data_log.to_csv(name, mode='w', header=True,
                          index=False)


def initialize_droplets_csv(name):
    """ Function to create an empty pandas.DataFrame and export it to CSV.
    This file will be used to log data droplets detected by a phase sensor.

    :param name: string
        Filename for the CSV
    """
    phase_data_log = pd.DataFrame(columns=['Time [s]'])
    phase_data_log.to_csv(name, mode='w', header=True,
                          index=False)


def convert_timestamp(timestamp):
    """ Function to convert the time stamp in a readable format.

    :param timestamp: integer
        Number of seconds since the *epoch* (for Unix: Jan 1, 1970 00:00:00)
    :return: string
        Date and time corresponding to the timestamp
    """
    return datetime.fromtimestamp(timestamp).strftime("%Y/%m/%d, %H:%M:%S.%f")


async def export_phase_sensor_data(name, data):
    """ Function to append a row to the CSV file with phase sensor data.

    :param name: string
        Filename for the CSV
    :param data: float
        Phase data to be exported (typically a reading from the phase sensor)
    """
    phase_data_log = pd.DataFrame(
        {
            'Time [s]': time.time(),
            'Time': [convert_timestamp(time.time())],
            'Phase': data
        }
    )
    phase_data_log.to_csv(name, mode='a', header=False, index=False)


async def export_droplets_data(name, data):
    """ Function to append a row to the CSV file with droplets data.

    :param name: string
        Filename for the CSV
    :param data: float
        Phase data to be exported (typically a reading from the phase sensor)
    """
    droplets_log = pd.DataFrame({'Time [s]': data}, index=[0])
    droplets_log.to_csv(name, mode='a', header=False, index=False)


if __name__ == "__main__":
    None
