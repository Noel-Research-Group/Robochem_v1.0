import asyncio
import pandas as pd

from List_connected_devices import find_port
from Phase_sensors.OPB350_IO_Arduino_sketch import PhaseSensor
from Phase_sensors.Phase_sensor_data_export import export_phase_sensor_data, \
    initialize_phase_sensor_csv, initialize_droplets_csv
import phase_sensor_CSV_naming


async def connect_to_board(port, sensor_id, log_name, frequency):
    """ Function to connect to a phase sensor board and start exporting data.

    This function will connect to a board and start exporting the phase
    detected by the phase sensors to corresponding csv file. The name of
    the csv file is given by a time stamp,the name of the board and the
    name of the phase sensor.
    The execution of this function will continue until actively broken.

    :param port: string
        The COM port the board is connected to.
    :param sensor_id: integer
        A single number identifying the phase sensor.
    :param log_name: string
        The name of the phase sensor for log
    :param frequency: float
        The time between two readings.
    :return:
        The phase (0 or 1) is written to the csv file until True loop
        actively broken.
    """
    board_phase_sensors = PhaseSensor(port, sensor_id, log_name)

    # create CSV file to log PS data
    filename1 = pd.read_csv(
        phase_sensor_CSV_naming.get_CSV_with_names_ps(),  # retrieve filename
        index_col=0
    )['0'][sensor_id]
    initialize_phase_sensor_csv(filename1)

    # create CSV files to log detected droplets
    filename2 = pd.read_csv(
        phase_sensor_CSV_naming.get_CSV_with_names_droplets(),
        index_col=0
    )['0'][sensor_id]
    initialize_droplets_csv(filename2)

    # to stop transients during start-up from being detected as bubbles
    # TODO adjust the sleep time
    await asyncio.sleep(2)

    while True:
        filename = pd.read_csv(
            phase_sensor_CSV_naming.get_CSV_with_names_ps(),
            index_col=0
        )['0'][sensor_id]
        await asyncio.sleep(frequency)
        await export_phase_sensor_data(
            filename,
            board_phase_sensors.get_phase()
        )


async def phase_sensor_1(freq=1):
    """Function used to connect to board phase_sensors_a and activate the
    export of the phase for each phase sensor.
    """
    await connect_to_board(
        port=find_port('PS1'),
        sensor_id=0,
        log_name='ps1',
        frequency=freq,
    )


async def phase_sensor_2(freq=1):
    """Function used to connect to board phase_sensors_a and activate the
    export of the phase for each phase sensor.
    """
    await connect_to_board(
        port=find_port('PS2'),
        sensor_id=1,
        log_name='ps2',
        frequency=freq,
    )


async def phase_sensor_3(freq=1):
    """Function used to connect to board phase_sensors_a and activate the
    export of the phase for each phase sensor.
    """
    await connect_to_board(
        port=find_port('PS3'),
        sensor_id=2,
        log_name='ps3',
        frequency=freq
    )


async def phase_sensor_4(freq=1):
    """Function used to connect to board phase_sensors_a and activate the
    export of the phase for each phase sensor.
    """
    await connect_to_board(
        port=find_port('PS4'),
        sensor_id=3,
        log_name='ps4',
        frequency=freq
    )


async def phase_sensor_5(freq=1):
    """Function used to connect to board phase_sensors_a and activate the
    export of the phase for each phase sensor.
    """
    await connect_to_board(
        port=find_port('PS5'),
        sensor_id=4,
        log_name='ps5',
        frequency=freq
    )


async def phase_sensor_6(freq=1):
    """Function used to connect to board phase_sensors_a and activate the
    export of the phase for each phase sensor.
    """
    await connect_to_board(
        port=find_port('PS6'),
        sensor_id=5,
        log_name='ps6',
        frequency=freq
    )


async def phase_sensor_7(freq=1):
    """Function used to connect to board phase_sensors_a and activate the
    export of the phase for each phase sensor.
    """
    await connect_to_board(
        port=find_port('PS7'),
        sensor_id=6,
        log_name='ps7',
        frequency=freq
    )


if __name__ == "__main__":
    phase_sensor_CSV_naming.create_list_of_CSV_names()

    # Executing export with asyncio.gather
    async def all_phase_sensors_export():
        """Coroutine for concurrent export of data from all phase sensors.
        """
        await asyncio.gather(
            phase_sensor_1(),
            phase_sensor_2(),
            phase_sensor_3(),
            phase_sensor_4(),
            phase_sensor_5(),
            phase_sensor_6(),
            phase_sensor_7(),
        )

    # asyncio.run(all_phase_sensors_export())

    # Executing export with asyncio.wait
    async def export_coro_wait():
        ps1 = asyncio.create_task(phase_sensor_1())
        ps2 = asyncio.create_task(phase_sensor_2())
        ps3 = asyncio.create_task(phase_sensor_3())
        ps4 = asyncio.create_task(phase_sensor_4())
        ps5 = asyncio.create_task(phase_sensor_5())
        ps6 = asyncio.create_task(phase_sensor_6())
        ps7 = asyncio.create_task(phase_sensor_7())

        tasks = [
            ps1, ps2, ps3, ps4,
            ps5, ps6, ps7,
        ]

        await asyncio.wait(
            tasks,
            return_when=asyncio.FIRST_COMPLETED
        )

    asyncio.run(export_coro_wait())
