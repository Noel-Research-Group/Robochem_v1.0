""" Script to analyze the data from a phase sensor.

D.Pintossi
2022-02-14 <3

Output:
    Plot saved in PNG format
        - PS signal (raw and filtered)
        - start/stop events
        - detected droplets/bubbles
        - detected reaction slug patterns
"""

from Phase_sensors.Droplet_identification import *
from phase_sensor_CSV_naming import get_your_abs_project_path
import matplotlib as plt

PROJECT_PATH = get_your_abs_project_path()
FILENAME = PROJECT_PATH + '\\Phase_sensor_DATA\\2022-05-30_T2038_PS3.csv'

FILTER_KERNEL = 7
# 1, 3, 5, 7, 9 --> spikes removed, small bubbles (5s) preserved
# 11, 13, 15,   --> spikes removed, BUT small bubbles lost

# Full dataset import
raw_test_data = import_phase_sensor_data(FILENAME)
complete_test_data = measure_droplets(
    data=import_phase_sensor_data(FILENAME),
    filter_kernel=FILTER_KERNEL,
)

# Limited import (remove first 100 s)
# raw_test_data = limited_import_phase_sensor_data(FILENAME, 180)
# complete_test_data = measure_droplets(
#     data=limited_import_phase_sensor_data(FILENAME, 180),
#     filter_kernel=FILTER_KERNEL,
# )

print('')
fig, axes = plt.subplots(4, 1, figsize=(12,7))
plt.subplots_adjust(hspace=1)  # adjust vertical spacing between plots

# 1. Phase data
axes[0].set_title(
    f'filter_kernel={FILTER_KERNEL}',
    fontweight='bold', pad=15,
)
axes[0].plot(
    raw_test_data['Time [s]'] - min(complete_test_data['Time [s]']),
    raw_test_data['Phase'],  # raw data
    label='Raw phase data',
)
axes[0].plot(
    complete_test_data['Time [s]'] - min(complete_test_data['Time [s]']),
    scipy.signal.medfilt(complete_test_data['Phase'], ),
    label='Filtered phase data',
    color='red',
)
axes[0].set_xlim(
    [
        0, max(complete_test_data['Time [s]'])
        - min(complete_test_data['Time [s]'])
    ]
)
axes[0].legend()

# 2. Start and stop detection (droplet)
axes[1].plot(
    complete_test_data['Time [s]'] - min(complete_test_data['Time [s]']),
    complete_test_data['Start_time'],
    label='Droplet start',
    color='green'
)
axes[1].plot(
    complete_test_data['Time [s]'] - min(complete_test_data['Time [s]']),
    complete_test_data['Stop_time'],
    label='Droplet stop',
    color='red'
)
axes[1].set_xlim(
    [
        0, max(complete_test_data['Time [s]'])
        - min(complete_test_data['Time [s]'])
    ]
)
axes[1].legend()

# 3. Drop and bubble size
axes[2].plot(
    complete_test_data['Time [s]'] - min(complete_test_data['Time [s]']),
    complete_test_data['Drop_size [s]'],
    label='Droplet size',
)
axes[2].plot(
    complete_test_data['Time [s]'] - min(complete_test_data['Time [s]']),
    complete_test_data['Bubble_size [s]'],
    label='Bubble size',
)
axes[2].set_xlim(
    [
        0, max(complete_test_data['Time [s]'])
        - min(complete_test_data['Time [s]'])
    ]
)
axes[2].legend()

# 4. Reaction drop
axes[3].plot(
    complete_test_data['Time [s]'] - min(complete_test_data['Time [s]']),
    complete_test_data['Reaction drop'],
    label='Reaction droplet',
)
axes[3].set_xlim(
    [
        0, max(complete_test_data['Time [s]'])
        - min(complete_test_data['Time [s]'])
    ]
)
axes[3].legend()

plt.savefig(
    PROJECT_PATH + '\\Phase_sensor_DATA\\' + FILENAME[-24:-4] + '_analysis.png',
    dpi=300
)
