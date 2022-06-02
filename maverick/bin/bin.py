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
        print(f"number_of_files: {number_of_files}")
        self.linear_bins[TimeSpectraKeys.file_index_array] = np.arange(0, number_of_files,
                                                                       file_index_value)
        print(self.linear_bins[TimeSpectraKeys.file_index_array])

