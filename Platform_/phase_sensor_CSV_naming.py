"""Functions to create list of files and corresponding files to store phase and droplet data in

"""
import datetime
import sys
import time
import platform
import os
import pandas as pd


# (NOT used, at least for now)
def find_folder_or_file(name='', search_path='.'):
    """Function to search for a specific file or directory within the
    search_path

    :param name: str
    name of the file or folder to be found
    :param search_path: str
    path where the file or folder is to be searched for
    :return: list
        path to the desired file or directory
    """
    result = []
    # Top-down search from root
    for root, dir, files in os.walk(search_path):
        if name in files or name in dir:
            result.append(os.path.join(root, name))
    return result


def get_your_abs_project_path():
    """Function to find the absolute path of the RoboChem project.
    (currently only works on Windows)

    :return: str
        absolute path of the project
    """
    if platform.system() != 'Windows':
        print('WARNING: The platform only works on Windows machines!')
        sys.exit()
    project_folder = os.path.abspath('..')
    if 'Platform_' not in project_folder:
        project_folder = project_folder + '\\Platform_\\'
    return project_folder


def get_CSV_with_names_ps():
    """Function to find the absolute path of CSV file with the name of all
    files where phase sensor data are saved.

    :return: str
        absolute path of the CSV file
    """
    list_of_names_path = (
            get_your_abs_project_path()
            + '/Phase_sensor_DATA'
            + '/List_of_CSV_names.csv'
    )
    return list_of_names_path


def get_CSV_with_names_droplets():
    """Function to find the absolute path of CSV file with the name of all
    files where phase sensor data are saved.

    :return: str
        absolute path of the CSV file with data file names
    """
    list_of_names_path = (
            get_your_abs_project_path()
            + '/Phase_sensor_DATA'
            + '/List_of_droplets_CSV_names.csv'
    )
    return list_of_names_path


def phase_sensor_csv_name(sensor):
    """Function to name the CSV files storing phase sensors data.

    :param sensor: integer
        Number identifying the phase sensor (1 - 7)
    :return: str
        absolute path of the CSV file with data
    """
    the_date = datetime.date.today()
    the_time = time.strftime("%H%M", time.localtime())
    absolute_name = (
        get_your_abs_project_path()
        + '/Phase_sensor_DATA/'
        + f'{the_date}_T{the_time}_PS{sensor}.csv'
    )
    return absolute_name


def droplets_csv_name(sensor):
    """Function to name the CSV files storing detected droplets data.

    :param sensor: integer
        Number identifying the phase sensor (1 - 7)
    :return: str
        absolute path of the CSV file with data
    """
    the_date = datetime.date.today()
    the_time = time.strftime("%H%M", time.localtime())
    absolute_name = (
        get_your_abs_project_path()
        + '/Phase_sensor_DATA'
        + f'/{the_date}_T{the_time}_droplets_PS{sensor}.csv'
    )
    return absolute_name


def create_list_of_CSV_names():
    """Function to create two CSV files containing the name of the CSV files
    to be used for logging data from the phase sensors export loops and
    droplet detection loops.

    :return None
    """
    # create dictionary of names for phase sensor files key: sensor number, value: filename
    CSV_names = {
        0: phase_sensor_csv_name(1),
        1: phase_sensor_csv_name(2),
        2: phase_sensor_csv_name(3),
        3: phase_sensor_csv_name(4),
        4: phase_sensor_csv_name(5),
        5: phase_sensor_csv_name(6),
        6: phase_sensor_csv_name(7),
    }

    # create dictionary of names for droplet data files, key: droplet number, value: filename
    droplets_CSV_names = {
        0: droplets_csv_name(1),
        1: droplets_csv_name(2),
        2: droplets_csv_name(3),
        3: droplets_csv_name(4),
        4: droplets_csv_name(5),
        5: droplets_csv_name(6),
        6: droplets_csv_name(7),
    }

    #convert distionaries to pandas dataframes then save them as CSV files
    names_df = pd.DataFrame.from_dict(CSV_names, orient='index')
    names_df.to_csv(
        get_your_abs_project_path()
        + '/Phase_sensor_DATA'
        + '/List_of_CSV_names.csv'
    )

    droplets_names_df = pd.DataFrame.from_dict(
        droplets_CSV_names, orient='index'
    )
    droplets_names_df.to_csv(
        get_your_abs_project_path()
        + '/Phase_sensor_DATA'
        + '/List_of_droplets_CSV_names.csv'
    )


if __name__ == '__main__':
    # print absolute path
    print(get_your_abs_project_path())

