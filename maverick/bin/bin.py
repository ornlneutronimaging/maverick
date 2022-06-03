import numpy as np

from ..session import SessionKeys
from ..utilities import TimeSpectraKeys
from ..utilities.get import Get


class Bin:

    linear_bins = {TimeSpectraKeys.tof_array: None,
                   TimeSpectraKeys.file_index_array: None,
                   TimeSpectraKeys.lambda_array: None}

    log_bins = {TimeSpectraKeys.tof_array: None,
                TimeSpectraKeys.file_index_array: None,
                TimeSpectraKeys.lambda_array: None}

    def __init__(self, parent=None):
        self.parent = parent

    def create_linear_file_index_bin_array(self, file_index_value):
        o_get = Get(parent=self.parent)
        list_of_folders_to_use = o_get.list_of_folders_to_use()
        number_of_files = len(self.parent.raw_data_folders[list_of_folders_to_use[0]]['list_files'])
        self.linear_bins[TimeSpectraKeys.file_index_array] = np.arange(0, number_of_files,
                                                                       file_index_value)

    def create_linear_axis(self, source_array=TimeSpectraKeys.file_index_array):

        if source_array == TimeSpectraKeys.file_index_array:
            file_index_array = self.linear_bins[TimeSpectraKeys.file_index_array]

            print(f"file_index_array: {file_index_array}")
            original_tof_array = np.array(self.parent.time_spectra[TimeSpectraKeys.tof_array])
            print(f"original_tof_array: {original_tof_array}")

            tof_array = [original_tof_array[int(_index)] for _index in file_index_array]
            self.linear_bins[TimeSpectraKeys.tof_array] = tof_array

            original_lambda_array = np.array(self.parent.time_spectra[TimeSpectraKeys.lambda_array])
            lambda_array = [original_lambda_array[int(_index)] for _index in file_index_array]
            self.linear_bins[TimeSpectraKeys.lambda_array] = lambda_array

            print(f"tof_array: {tof_array}")
            print(f"lambda_array: {lambda_array}")