"""
Diego Pintossi, Zhenghui Wen
Noël Research Group
Van 't Hoff Institute for Molecular Sciences (HIMS)
Universiteit van Amsterdam (UvA)

2021-07-28

Function to set up logging to multiple files.

Source:
https://stackoverflow.com/questions/11232230/logging-to-two-files-with-different-settings

"""

import logging
import datetime
import time
from phase_sensor_CSV_naming import get_your_abs_project_path

def setup_logger(name, log_file, level=logging.DEBUG):
    """Function to set up Logger objects sharing the same configuration.
    Logs are saved in:
        .../RoboChem_auto-optimization-platform/Activity_logs

    :param name: string
        Name of the Logger object
    :param log_file: string
        Filename of the log
    :param level: logging level
        Lowest level to be registered in the log
        (e.g., logging.DEBUG)
    :return:
        Logger object
    """
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    the_date = datetime.date.today()
    the_time = time.strftime("%H%M", time.localtime())
    timestamp = f'{the_date}_T{the_time}_'

    complete_filename = (
        get_your_abs_project_path()
        + '/Activity_logs/'
        + timestamp
        + log_file
    )
    handler = logging.FileHandler(complete_filename)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

if __name__ == "__main__":
    logger = logging.basicConfig(filename='logger.log', level=logging.INFO)
    logger_2 = setup_logger("logger_2", "log2.log", level=logging.DEBUG)
    logger_2.debug("Debug message for logger_2")
    logger_3 = setup_logger("logger_3", "log3.log", level=logging.INFO)
    logger_3.debug("Debug message for logger_3 that should not appear")
    logger_3.error("Error message for logger_3")