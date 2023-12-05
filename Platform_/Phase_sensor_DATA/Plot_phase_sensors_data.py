"""Script to visualize the phase sensors data

D.Pintossi, Aidan Slattery
2022-01-21
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd


def make_filenames_OLD(time_string):
    """Script to obtain the filename for the CSV files with phase sensors data.

    :param time_string: string
        String describing the date and time of creation of the CSV file of
        interest (e.g., '2022-01-24_T1252')
    :return: dict
        Dictionary containing the CSV file names for PS1 to PS7
    """
    return {
        'PS1': time_string + '_phase_sensors_A_PS1.csv',
        'PS2': time_string + '_phase_sensors_A_PS2.csv',
        'PS3': time_string + '_phase_sensors_A_PS3.csv',
        'PS4': time_string + '_phase_sensors_B_PS4.csv',
        'PS5': time_string + '_phase_sensors_B_PS5.csv',
        'PS6': time_string + '_phase_sensors_B_PS6.csv',
        'PS7': time_string + '_phase_sensors_B_PS7.csv',
    }


def make_filenames(time_string):
    """Script to obtain the filename for the CSV files with phase sensors data.

    :param time_string: string
        String describing the date and time of creation of the CSV file of
        interest (e.g., '2022-01-24_T1252')
    :return: dict
        Dictionary containing the CSV file names for PS1 to PS7
    """
    return {
        'PS1': time_string + '_PS1.csv',
        'PS2': time_string + '_PS2.csv',
        'PS3': time_string + '_PS3.csv',
        'PS4': time_string + '_PS4.csv',
        'PS5': time_string + '_PS5.csv',
        'PS6': time_string + '_PS6.csv',
        'PS7': time_string + '_PS7.csv',
    }


def subplot_phase_sensor(axes, phase_sensor):
    """Function to fill a subplot with phase sensor data.

    :param axes: matplotlib.pyplot axes Object
        Axes object (e.g., ax1 for subplot1 (top one))
    :param phase_sensor: string
        Name of phase sensor (e.g., 'PS1')
    """
    # try/except construct to handle missing datasets
    # e.g., plotting data for less than 7 sensors
    try:
        # Import data
        df = pd.read_csv(FILENAMES[phase_sensor])  # not a great way to do this
        time = df['Time [s]']
        time = time - min(time)
        phase = df['Phase']
        # Set axes limits
        axes.set_xlim(min(time), max(time))
        axes.set_ylim(-0.1, 1.1)
        labels = axes.get_yticks().tolist()
        axes.yaxis.set_major_locator(mticker.FixedLocator(labels))
        labels[1] = 'Gas'
        labels[2] = 'Liquid'
        axes.set_yticklabels(labels)
        # Plot data
        axes.plot(
            time,
            phase,
            linewidth=1,
            marker='o',
            markersize=2,
            label=phase_sensor
        )
        # Add legend
        axes.legend(loc=3)
    except (FileNotFoundError, ValueError):
        # FileNotFoundError --> missing CSV file
        # ValueError --> empty CSV file (headers only)
        pass


# Create 7 plots
fig, ax = plt.subplots(7, 1, figsize=(12, 11))

# Adjust vertical spacing between subplots
plt.subplots_adjust(
    hspace=1
)

# Timestamp of the desired dataset
TIMESTAMP = '2022-01-28_T1657'
FILENAMES = make_filenames(TIMESTAMP)

# Set the axes titles
ax[0].set_title(TIMESTAMP, fontweight='bold', pad=15)
ax[6].set_xlabel('Time [s]', fontweight='bold', labelpad=12)
ax[3].set_ylabel('Phase [-]', fontweight='bold', labelpad=12)

# Add data to the subplots
for i, j in zip(ax, FILENAMES.keys()):
    subplot_phase_sensor(i, j)

# Display the plots
# plt.show()

# Save plot
fig.savefig(
    f'../Phase_sensor_DATA/{TIMESTAMP}.png',
    dpi=300
)

if __name__ == '__main__':
    None
