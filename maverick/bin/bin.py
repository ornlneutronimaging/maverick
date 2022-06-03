import numpy as np
import logging

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
        self.logger = logging.getLogger('maverick')

    def create_linear_file_index_bin_array(self, file_index_value):
        o_get = Get(parent=self.parent)
        list_of_folders_to_use = o_get.list_of_folders_to_use()
        number_of_files = len(self.parent.raw_data_folders[list_of_folders_to_use[0]]['list_files'])
        _array = np.arange(0, number_of_files, file_index_value)

        # there is a file index outside the range
        if _array[-1] < (number_of_files-1):
            _array = np.append(_array, number_of_files-1)

        self.linear_bins[TimeSpectraKeys.file_index_array] = _array

    def create_linear_tof_bin_array(self, tof_value):
        original_tof_array = np.array(self.parent.time_spectra[TimeSpectraKeys.tof_array])
        left_value = 0
        right_value = tof_value
        _linear_bins = []
        while right_value < original_tof_array[-1]:
            _linear_bins.append(left_value)
            left_value = right_value
            right_value += tof_value
        _linear_bins.append(right_value)
        self.linear_bins[TimeSpectraKeys.tof_array] = np.array(_linear_bins)

    def create_linear_axis(self, source_array=TimeSpectraKeys.file_index_array):
        if source_array == TimeSpectraKeys.file_index_array:
            file_index_array = self.linear_bins[TimeSpectraKeys.file_index_array]

            original_tof_array = np.array(self.parent.time_spectra[TimeSpectraKeys.tof_array])
            tof_array = [original_tof_array[int(_index)] for _index in file_index_array]
            self.linear_bins[TimeSpectraKeys.tof_array] = tof_array

            original_lambda_array = np.array(self.parent.time_spectra[TimeSpectraKeys.lambda_array])
            lambda_array = [original_lambda_array[int(_index)] for _index in file_index_array]
            self.linear_bins[TimeSpectraKeys.lambda_array] = lambda_array

        elif source_array == TimeSpectraKeys.tof_array:
            pass
            # tof_array = self.linear_bins[TimeSpectraKeys.tof_array]
            # original_tof_array = self.parent.time_spectra[TimeSpectraKeys.tof_array]
            #
            # original_file_index_array = np.array(self.parent.time_spectra[TimeSpectraKeys.file_index_array])
            # file_index_array = []
            # _index = 0
            # _tof_bin_right = tof_array[1]
            # for _tof in tof_array:
            #     if _tof < _tof_bin_right:
            #         continue
            #     file_index_array.append(_index)
            #     _index += 1
            # self.linear_bins[TimeSpectraKeys.file_index_array] = file_index_array

            original_lambda_array = np.array(self.parent.time_spectra[TimeSpectraKeys.lambda_array])


    def get_linear_delta_file_index(self):
        return self._get_linear_delta(key=TimeSpectraKeys.file_index_array)

    def get_linear_delta_tof(self):
        return self._get_linear_delta(key=TimeSpectraKeys.tof_array)

    def get_linear_delta_lambda(self):
        return self._get_linear_delta(key=TimeSpectraKeys.lambda_array)

    def _get_linear_delta(self, key=TimeSpectraKeys.file_index_array):
        return self.linear_bins[key][1] - self.linear_bins[key][0]
