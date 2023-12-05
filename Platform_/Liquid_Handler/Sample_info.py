"""
Aidan Slattery, Zhenghui Wen
Noël Research Group
Van 't Hoff Institute for Molecular Sciences (HIMS)
Universiteit van Amsterdam (UvA)

Sample info class for getting the sample information
from Excel file (Sample info in GX-241.xlsx)
"""
import copy
import os
from ast import literal_eval

import pandas as pd
import numpy as np
import collections
import sys
from Logging_organizer.Logging_Setting import setup_logger
from phase_sensor_CSV_naming import get_your_abs_project_path


class SampleInfo(object):
    """Class for extracting the sample info from the Excel files
        - Sample info in GX-241.xlsx
        - XYZ_Values.xlsx
    """

    def __init__(self, filepath):
        """Class initialization.

        :param filepath: str
            relative filepath of the Excel file with all the info on the samples
        """
        self.logger = setup_logger('Sample_Info_logger', 'Sample_info.log')
        self.filepath = filepath
        # Dictionary to store the information about each vial
        self.sample_dict = collections.defaultdict(dict)

        # Dictionary to store information about vials grouped by their content
        self.sample_dict_order = collections.defaultdict(dict)

        # Dictionaries to store information about vials in each rack
        self.sample_dict_335S = {}
        self.sample_dict_338S = {}

        # Dictionary to store the coordinates of all vials
        self.sample_location_335S = {}
        self.sample_location_338S = {}

        # Dictionaries used to temporarily store info about each vial
        self.sample_vial_335S = {}
        self.sample_vial_338S = {}

        # List to store all sample names
        # (incl. concentration, position, and vial number)
        self.sample_info_335S = []
        self.sample_info_338S = []

        # Dictionary to store sample names
        # (without concentration, position,or vial number)
        self.sample_name_dict = {}

        # Dictionary to store the number of vials for each chemical
        self.sample_bottles = {}

        # ???
        self.working_sample_sequence = []
        self.working_sample_bottle = []

        # ???
        self.current_sample_volume = []

        # ???
        self.total_used_sample_volume = []

        # Import the sample names into a Pandas DataFrame
        self.sample = pd.read_excel(
            # get_your_abs_project_path() + #this worked when the files were added to the Platform/ not in your repo
            self.filepath,
            engine='openpyxl',
            keep_default_na=False
        )
        # Reference (not a copy) to the sample names for rack 338S
        self.sample_value_338S = self.sample.iloc[6:22, 1:5]
        # Reference (not a copy) to the sample names for rack 335S
        self.sample_value_335S = self.sample.iloc[6:18, 6:10]

        # Import the XYZ coordinates corresponding to the positions on the racks
        self.coordinate = pd.read_excel(
            get_your_abs_project_path()
            + "Liquid_Handler\\XYZ_Values.xlsx",
            engine='openpyxl', keep_default_na=False
        )
        # Reference (not a copy) to the XYZ coordinates for rack 338S
        self.coordinate_value_338S = self.coordinate.iloc[6:22, 1:5]
        # Reference (not a copy) to the XYZ coordinates for rack 335S
        self.coordinate_value_335S = self.coordinate.iloc[6:18, 6:10]
        self.inverted_sample_dict = {}
        self.volume_taken = 0


    def get_sample_name(self):
        """Get the sample names list from Excel (at the bottom of the template).

        :return: dict
            e.g., {'Solvent': ['MeCN'], 'Substrate A': ['SampleA'],
            'Catalyst':['a', 'b']...}
        """
        sample_list = self.sample.iloc[26:38, 1:10]

        for column in range(sample_list.shape[1]):
            # Get the key of sample_name_dict
            SAMPLE_name = sample_list.values[0, column]
            if SAMPLE_name == '':
                break
            # Direct slice the column from each SAMPLE_name to
            # get the value for the sample_name_dict
            reagent_column = sample_list.iloc[1:, column]
            reagent_list = []
            # Remove the empty value from the reagent_column
            for sample in reagent_column:
                if sample != '':
                    reagent_list.append(sample)
            self.sample_name_dict[SAMPLE_name] = reagent_list

        self.logger.info('The extracted sample names are:')
        for name in self.sample_name_dict:
            self.logger.info(f'{name}')

        print('sample_name_dict:', self.sample_name_dict)
        return self.sample_name_dict # todo maybe need list with keys

    def get_sample_info(self):
        """Transfer the sample_info in the Excel files to a dictionary including
        all the information of samples.

        The structure of the dictionary is:
        {
            'sample_name': {
                'sample_name-i': {
                    'sequence': ___,       # bottle number
                    'concentration': ___,  # concentration of the stock solution
                    'position': ___,       # XYZ coordinates of the bottle
                    'volume': ___          # volume in the vial
                    }
            }
        }

        :return: dict
            ???
        """
        # Get the sample info from 335S rack
        for row in range(self.sample_value_335S.shape[0]):
            for column in range(self.sample_value_335S.shape[1]):
                sample_info = self.sample_value_335S.values[row, column]
                # Check that the corresponding cell is not empty
                if sample_info != '':
                    # fetch coordinates for the vial and store in dict
                    self.sample_location_335S[sample_info] = \
                        self.coordinate_value_335S.values[row, column]
                    # fetch name of the vial and store in list
                    self.sample_info_335S.append(sample_info)

        # Extract information encoded in the sample names (rack 335S)
        #   (looping over all vials)
        for sample_info in self.sample_info_335S:
            sample_name = sample_info.split('_')[0]
            # Vial ID for a given substance
            self.sample_vial_335S['sequence'] = \
                sample_info.split('_')[0].split('-')[1]
            # Concentration of the stock solution in the vial
            self.sample_vial_335S['concentration'] = sample_info.split('_')[1]
            # XYZ coordinates of the vial
            self.sample_vial_335S['position'] = \
                self.sample_location_335S[sample_info]
            # volume of stock solution in the vial
            self.sample_vial_335S['volume'] = sample_info.split('_')[2]
            self.sample_dict_335S[sample_name] = self.sample_vial_335S
            # print(self.sample_dict_335S)
            self.inverted_sample_dict[self.sample_vial_335S['position']] = [
                sample_name, self.sample_vial_335S['concentration'],
                self.sample_vial_335S['volume']]
            self.sample_vial_335S = {}


        # Get the sample info from 338S rack
        for row in range(self.sample_value_338S.shape[0]):
            for column in range(self.sample_value_338S.shape[1]):
                sample_info = self.sample_value_338S.values[row, column]
                if sample_info != '':
                    # fetch coordinates for the vial and store in dict
                    self.sample_location_338S[sample_info] = \
                        self.coordinate_value_338S.values[row, column]
                    # fetch name of the vial and store in list
                    self.sample_info_338S.append(sample_info)

        # Extract information encoded in the sample names (rack 338S)
        #   (looping over all vials)
        for sample_info in self.sample_info_338S:
            sample_name = sample_info.split('_')[0]
            self.sample_vial_338S['sequence'] = \
                sample_info.split('_')[0].split('-')[1]
            self.sample_vial_338S['concentration'] = sample_info.split('_')[1]
            self.sample_vial_338S['position'] = \
                self.sample_location_338S[sample_info]
            self.sample_vial_338S['volume'] = sample_info.split('_')[2]
            self.sample_dict_338S[sample_name] = self.sample_vial_338S
            self.inverted_sample_dict[self.sample_vial_338S['position']] = [
                sample_name, self.sample_vial_338S['concentration'],
                self.sample_vial_338S['volume']]
            self.sample_vial_338S = {}

        # Merge the sample info from two racks into one sample dictionary
        self.sample_dict = self.sample_dict_335S.copy()
        self.sample_dict.update(self.sample_dict_338S)
        # print('sample_dict_key is :', self.sample_dict.keys())
        # print('sample_dict is :', self.sample_dict)
        # Restructure the sample dictionary into an ordered sample dictionary
        for SAMPLE_NAME in self.sample_name_dict.keys():
            # print('SAMPLE_NAME', SAMPLE_NAME)
            for vial in self.sample_dict.keys():
                sample_without_sequence = vial.split('-')[0]
                if [sample_without_sequence] == self.sample_name_dict[
                    SAMPLE_NAME]:
                    self.sample_dict_order[SAMPLE_NAME][vial] = \
                    self.sample_dict[vial]
                else:
                    if sample_without_sequence in self.sample_name_dict[
                        SAMPLE_NAME]:
                        self.sample_dict_order[SAMPLE_NAME][vial] = \
                            self.sample_dict[vial]

        self.logger.info('The extracted information about the vials is:')
        for info in self.sample_dict_order.keys():
            self.logger.info(f'{self.sample_dict_order[info]}')
        # print(self.sample_dict_order)
        # print('sample_dict_order:', self.sample_dict_order)
        return self.sample_dict_order

    def initial_sample_info(self):
        """Function to get the initial sample info.

        :return: tuple
            List of active vials, volume in the active vials
        """
        # Loop over the different chemical species in the vials
        for i in self.sample_name_dict.keys():

            if len(self.sample_name_dict[i]) == 1:
                vial = self.sample_name_dict[i][0]
                self.working_sample_bottle.append(vial + '-0')
                volume_value = self.sample_dict_order[i][vial + '-0'][
                    'volume']
                self.current_sample_volume.append(float(volume_value))
                self.working_sample_sequence.append(0)
                self.total_used_sample_volume.append(0)
            else:
                for sample in self.sample_name_dict[i]:
                    self.working_sample_bottle.append(sample + '-0')
                    volume_value = self.sample_dict_order[i][sample + '-0'][
                        'volume']
                    self.current_sample_volume.append(float(volume_value))
                    self.working_sample_sequence.append(0)
                    self.total_used_sample_volume.append(0)

        self.logger.info(f"The first vials to be used are: "
                         f"{self.working_sample_bottle}.")

        # print('working_sample_bottle:', self.working_sample_bottle, '\n'
        #       'current_sample_volume:', self.current_sample_volume, '\n'
        #       'working_sample_sequence:', self.working_sample_sequence, '\n'
        #       'total_used_sample_volume: ', self.total_used_sample_volume)

        return self.working_sample_bottle, self.current_sample_volume

    def get_sample_bottles_number(self):
        """Functions to get how many bottles of the same sample.

        :return: dict
            Number of vials for each chemical
        """
        # Loop over the different chemical species in the vials
        sample_name_random = []
        for sample_i in self.sample_dict.keys():
            sample_name_random.append(sample_i.split('-')[0])
        # print('sample_name_random:', sample_name_random)
        for SAMPLE_NAME_j in self.sample_name_dict.keys():
            if len(self.sample_name_dict[SAMPLE_NAME_j]) == 1:
                sample_name = self.sample_name_dict[SAMPLE_NAME_j][0]
                self.sample_bottles[sample_name] = \
                    len(self.sample_dict_order[SAMPLE_NAME_j].keys())
            else:
                for sample_small in self.sample_name_dict[SAMPLE_NAME_j]:
                    self.sample_bottles[sample_small] = \
                        sample_name_random.count(sample_small)

        self.logger.info(f"The number of sample bottles are: "
                         f"{self.sample_bottles}.")

        # print('Sample_bottle:', self.sample_bottles)
        return self.sample_bottles

    def update_excel(self, sample_info_handler):
        split_path = self.filepath.split('/')  # get the last for the excel file
        print(split_path)
        df_large = pd.read_excel(f'{split_path[-1]}',
                                 engine='openpyxl',
                                 keep_default_na=False
                                 )
        # sample_value_338S = df.iloc[6:22, 1:5]  # TODO: include in far away future
        df = df_large.iloc[6:18, 6:10]
        for i, condition in enumerate(sample_info_handler):
            # Connect position on liquid handler to an ID - condition[0] = pos
            sample_ID = self.inverted_sample_dict[condition[0]]
            sample_to_take = condition[1]
            sample = sample_ID[0]
            #            0   1  2
            row = df.apply(lambda row: row.astype(str).str.contains(sample).any(),
                           axis=1).values
            row_position = np.where(row == True)[0][0]
            column = df.apply(
                lambda column: column.astype(str).str.contains(sample).any(),
                axis=0).values
            column_position = np.where(column == True)[0][0]
            # g = df[df.eq('MeCN-4_0_4').any(1)]
            sample_list = [sample]
            conc = sample_ID[1]
            sample_list.append(conc)
            volume = str(round(float(sample_ID[2]) - float(sample_to_take), 4))
            sample_list.append(volume)
            # sample_splits = sample.split('_')
            # sample_splits[2] = str(float(sample_splits[2]) - sample_to_take)
            new_volume_string = '_'.join(sample_list)
            df.iloc[row_position, column_position] = new_volume_string
        df_large.iloc[6:18, 6:10] = df
        # add a newline in the 1st row

        df1 = pd.DataFrame([[np.nan] * len(df_large.columns)],
                           columns=df_large.columns)
        df_large = pd.concat([df1,df_large], ignore_index=True) #changed as append is deprecated
        df_large.to_excel(f'{split_path[-1]}', header=False, index=False)

    def prepare_sample_info(self, chemical_space):
        """Functions to transfer the reaction conditions from BO to
        sample locations and volumes, which can be read by liquid handler.

        :param conditions: list of numpy values
            comes from BO, list, e.g. ['A', 0.1, 'B', 2, 'C', 0.01, 5]
            order for the condition list: ['sub_A', subA_con, 'sub_B',
             subB_equiv, 'catal', catal_loading, residence time]
        :return: dict
            self.sample_info
        """

        conditions_np = copy.deepcopy(chemical_space)  # create a clone as not to have
        # the same filepointer
        conditions = literal_eval(repr(conditions_np))# This is used to make sure that the type of the items always is normal python types
        conditions = self.solvent_identity(conditions)
        print(conditions)
        slug_size = 0.65
        sample_info_handler = []
        single_sample_info = []

        total_vol = 0
        volumes = []
        working_sub_A_sample = ''
        working_sample_i = ''
        print('Sample bottle')
        print(self.working_sample_bottle)
        print(conditions)
        for working_sample in self.working_sample_bottle:
            if conditions[0] == working_sample.split('-')[0]:
                working_sub_A_sample = working_sample

        sample_conc_A = conditions[1]
        for i, condition in enumerate(conditions):
            # get the concentration of stock solution of compound sub_A

            conc_A = float(
                self.sample_dict_order[list(self.sample_name_dict.keys())[0]][
                    working_sub_A_sample]['concentration']) / 1000

            if i == 0:
                total_vol = (float(sample_conc_A) * slug_size) / conc_A
                volumes.append(total_vol)
                conditions.remove(conditions[i + 1])

            elif i != 0:
                if type(condition) == str:
                    # get the working sample vial for compound i
                    for working_sample in self.working_sample_bottle:
                        if condition == working_sample.split('-')[0]:
                            working_sample_i = working_sample
                    # get the concentration of stock solution of compound i
                    conc_reagent = (float(self.sample_dict_order[list(
                        self.sample_name_dict.keys())[i]][working_sample_i][
                                              'concentration']) / 1000)
                    # calculate the required volume of compound i
                    vol = (slug_size * float(sample_conc_A) * float(
                        conditions[i + 1]) / conc_reagent)
                    volumes.append(vol)
                    total_vol += vol
                    conditions.remove(conditions[i + 1])
                # else: isn't this a completely unnecessary Else?
                #     pass

        reagent_volume = sum(volumes)
        if reagent_volume >= slug_size:
            raise Exception('Reagent selection impossible'
                            '\nPlease reduce the loadings of reagents or '
                            'increase the concentration of the stock solutions')
        solvent_volume = slug_size - reagent_volume
        volumes.append(solvent_volume)
        sample_volume = np.array(volumes)
        # print(volumes)



        #######################################################################
        # update the volumes of working samples
        for i, condition in enumerate(conditions):
            if type(condition) == str:
                for j, working_sample in enumerate(self.working_sample_bottle):
                    if condition == working_sample.split('-')[0]:
                        self.current_sample_volume[j] -= \
                            sample_volume.tolist()[i]
                        self.current_sample_volume[j] = \
                            round(self.current_sample_volume[j], 4)

                        for reagent_num in range(self.sample_bottles[condition]):
                            if self.current_sample_volume[j] > 0.15:
                                # Get XYZ coordinates
                                single_sample_info.append(
                                    self.sample_dict[
                                        self.working_sample_bottle[j]]['position']
                                )
                                # Get volume
                                single_sample_info.append(
                                    round(sample_volume.tolist()[i], 4)
                                )
                                sample_info_handler.append(single_sample_info)
                                self.total_used_sample_volume[j] += \
                                    sample_volume.tolist()[i]
                                self.total_used_sample_volume[j] = \
                                    round(self.total_used_sample_volume[j], 4)
                                single_sample_info = []
                                break
                            else:
                                # actual needed value is
                                self.working_sample_sequence[j] += 1
                                reagent_num += 1

                                if reagent_num == self.sample_bottles[condition]:
                                    self.logger.error(
                                            f"{condition} are finished. "
                                            f"Please add them asap")
                                    print(f"{condition} are finished. "
                                              f"Please add them asap")
                                    sys.exit()
                                else:
                                        self.working_sample_bottle[j] = \
                                        condition + '-' + \
                                        str(self.working_sample_sequence[j])
                                    # Update the residual volume
                                        self.current_sample_volume[j] = float(
                                            self.sample_dict
                                            [self.working_sample_bottle[j]]['volume'])
                                        self.current_sample_volume[j] -= \
                                            sample_volume.tolist()[i]
                                        self.current_sample_volume[j] = \
                                            round(self.current_sample_volume[j], 4)

        ########################################################################
        # check if extra solvent is needed for preparing sample
        if solvent_volume > 0:
            # print(self.working_sample_bottle)
            # print(self.working_sample_sequence)
            # print(self.sample_dict)
            solvent_name = self.sample_name_dict['Solvent'][0]
            # print(self.working_sample_bottle)
            for i, working_sample in enumerate(self.working_sample_bottle):
                if solvent_name == working_sample.split('-')[0]:
                    # volume of the solvent is the last element of the list
                    self.current_sample_volume[i] -= \
                        sample_volume.tolist()[-1]
                    self.current_sample_volume[i] = \
                        round(self.current_sample_volume[i], 4)

                    for solvent_num in range(self.sample_bottles[solvent_name]):
                        if self.current_sample_volume[i] > 0.15:
                            # Get XYZ coordinates
                            single_sample_info.append(
                                self.sample_dict[
                                    self.working_sample_bottle[i]]['position']
                            )
                            # Get volume
                            single_sample_info.append(
                                round(sample_volume.tolist()[-1], 4)
                            )
                            sample_info_handler.append(single_sample_info)
                            self.total_used_sample_volume[i] += \
                                sample_volume.tolist()[-1]
                            self.total_used_sample_volume[i] = \
                                round(self.total_used_sample_volume[i], 4)
                            single_sample_info = []
                            break
                        else:
                            # actual needed value is
                            self.working_sample_sequence[i] += 1
                            solvent_num += 1

                            if solvent_num == self.sample_bottles[solvent_name]:
                                self.logger.error(f"{solvent_name} are finished. "
                                                  f"Please add them asap")
                                print(f"{solvent_name} are finished. "
                                                  f"Please add them asap")
                                sys.exit()

                            else:
                               # Update the list of active vials
                                self.working_sample_bottle[i] = \
                                    solvent_name + '-' + \
                                    str(self.working_sample_sequence[i])
                                # Update the residual volume
                                self.current_sample_volume[i] = float(
                                    self.sample_dict
                                    [self.working_sample_bottle[i]]['volume'])
                                self.current_sample_volume[i] -= \
                                    sample_volume.tolist()[-1]
                                self.current_sample_volume[i] = \
                                    round(self.current_sample_volume[i], 4)

        # print(sample_info_handler)
        self.update_excel(sample_info_handler)
        self.logger.info(f"Sample info for LH is {sample_info_handler}")
        return sample_info_handler


    def solvent_identity(self, X):
        if 'NaDT' in X:
            for i in range(len(X)):
                if i % 2 == 0:
                    X[i] = X[i] + '1'
        else:
            pass
        return X

if __name__ == '__main__':
    # None
    FILEPATH = '/Liquid_Handler/example.xlsx'
    # FILEPATH = '/Liquid_Handler/Sample info in GX-241.xlsx'
    sample = SampleInfo(FILEPATH)
    # Initial the sample info
    sample.get_sample_name()
    sample.get_sample_info()
    sample.initial_sample_info()
    sample.get_sample_bottles_number()