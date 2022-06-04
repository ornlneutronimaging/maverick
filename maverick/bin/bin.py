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
        """this method create the linear TOF bins array"""
        original_tof_array = np.array(self.parent.time_spectra[TimeSpectraKeys.tof_array])
        linear_bins = self._create_generial_linear_array(stepping=tof_value,
                                                         original_array=original_tof_array)
        self.linear_bins[TimeSpectraKeys.tof_array] = linear_bins

    def create_linear_lambda_array(self, lambda_value):
        """this method create the linear lambda array"""
        original_lambda_array = np.array(self.parent.time_spectra[TimeSpectraKeys.lambda_array])
        linear_bins = self._create_generial_linear_array(stepping=lambda_value,
                                                         original_array=original_lambda_array)
        self.linear_bins[TimeSpectraKeys.lambda_array] = linear_bins

    def _create_generial_linear_array(self, stepping=None, original_array=None):
        """
        generic function used to create a linear bin array

        :param stepping: stepping bin value
        :param original_array: original array that will be used to determine when to stop
        :return: the linear bin array
        """
        left_value = 0
        right_value = stepping
        _linear_bins = []
        while right_value < original_array[-1]:
            _linear_bins.append(left_value)
            left_value = right_value
            right_value += stepping
        _linear_bins.append(right_value)
        return np.array(_linear_bins)

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
            tof_array = self.linear_bins[TimeSpectraKeys.tof_array]
            original_tof_array = self.parent.time_spectra[TimeSpectraKeys.tof_array]

            index_of_bins_in_original_array = \
                Bin.create_index_of_bins_in_original_array(bin_array=tof_array,
                                                           original_array=original_tof_array)
            self.linear_bins[TimeSpectraKeys.file_index_array] = index_of_bins_in_original_array

            original_lambda_array = np.array(self.parent.time_spectra[TimeSpectraKeys.lambda_array])
            lambda_array = [original_lambda_array[int(_index)] for _index in index_of_bins_in_original_array]
            self.linear_bins[TimeSpectraKeys.lambda_array] = lambda_array

        elif source_array == TimeSpectraKeys.lambda_array:
            lambda_array = self.linear_bins[TimeSpectraKeys.lambda_array]
            original_lambda_array = self.parent.time_spectra[TimeSpectraKeys.lambda_array]

            index_of_bins_in_original_array = \
                Bin.create_index_of_bins_in_original_array(bin_array=lambda_array,
                                                           original_array=original_lambda_array)
            self.linear_bins[TimeSpectraKeys.file_index_array] = index_of_bins_in_original_array

            original_tof_array = np.array(self.parent.time_spectra[TimeSpectraKeys.tof_array])
            tof_array = [original_tof_array[int(_index)] for _index in index_of_bins_in_original_array]
            self.linear_bins[TimeSpectraKeys.tof_array] = tof_array

        else:
            raise NotImplementedError(f"Bin parameter {source_array} not implemented!")

    @staticmethod
    def create_index_of_bins_in_original_array(bin_array=None, original_array=None):
        """
        This method determine the index of the various bin in the original array. This will then be
        used to find the equivalent location in the other arrays, for example lambda and file_index when
        the bin_array was calculated for tof

        :param bin_array: bin array created (for example lambda_bin_array)
        :param original_array: original array (for example the original_lambda_array)
        :return: an array of the index of each bin
        """
        index_of_bins_in_original_array = [0]
        for _bin in bin_array:
            result = np.where(_bin <= original_array)
            try:
                index_of_bins_in_original_array.append(result[0][0])
            except IndexError:  # exception is value is outside of original range
                pass
        return index_of_bins_in_original_array

    def get_linear_delta_file_index(self):
        return self._get_linear_delta(key=TimeSpectraKeys.file_index_array)

    def get_linear_delta_tof(self):
        return self._get_linear_delta(key=TimeSpectraKeys.tof_array)

    def get_linear_delta_lambda(self):
        return self._get_linear_delta(key=TimeSpectraKeys.lambda_array)

    def _get_linear_delta(self, key=TimeSpectraKeys.file_index_array):
        return self.linear_bins[key][1] - self.linear_bins[key][0]

    def get_linear_file_index(self):
        return self.linear_bins[TimeSpectraKeys.file_index_array]

    def get_linear_tof(self):
        return self.linear_bins[TimeSpectraKeys.tof_array]

    def get_linear_lambda(self):
        return self.linear_bins[TimeSpectraKeys.lambda_array]
