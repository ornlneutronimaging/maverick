import numpy as np
import logging

from ..utilities import TimeSpectraKeys
from ..utilities.get import Get


class LinearBin:

    linear_bins = {TimeSpectraKeys.tof_array: None,
                   TimeSpectraKeys.file_index_array: None,
                   TimeSpectraKeys.lambda_array: None}

    def __init__(self, parent=None, source_array=TimeSpectraKeys.file_index_array):
        self.parent = parent
        self.source_array = source_array
        self.logger = logging.getLogger('maverick')

    def create_linear_file_index_bin_array(self, bin_value=1):
        """creates the array of bins
        output will look like [[0,1],[2,3],[4,5]...]
        """
        original_array = np.array(self.parent.time_spectra[self.source_array])

        if self.source_array == TimeSpectraKeys.file_index_array:
            number_of_files = len(original_array)
            new_index_array = np.arange(0, number_of_files, bin_value)

            linear_file_index_bin_array = [[] for _ in np.arange(len(new_index_array))]
            for _file_index, _bin in enumerate(original_array):
                result = np.where(_bin >= new_index_array)
                index = result[0][-1]
                linear_file_index_bin_array[index].append(_file_index)

            print(f"linear_file_index_bin_array: {linear_file_index_bin_array}")

            # array_of_bins = [[] for _ in np.arange(len(new_index_array)-1)]
            # for _index, _bin in enumerate(linear_file_index_bin_array[:-1]):
            #     array_of_bins[_index] = [linear_file_index_bin_array[_index][0],
            #                              linear_file_index_bin_array[_index+1][0]]
            # # if len(linear_file_index_bin_array[-1]) > 2:
            # array_of_bins[-1] = [linear_file_index_bin_array[-1][0], linear_file_index_bin_array[-1][-1] + 1]
            # # else:
            # #     array_of_bins[-1] = [linear_file_index_bin_array[-1][0], linear_file_index_bin_array[-1][-1] + 1]

            # print(f"array_of_bins: {array_of_bins}")

        elif self.source_array == TimeSpectraKeys.tof_array:
            original_tof_array = np.array(self.parent.time_spectra[TimeSpectraKeys.tof_array])

            new_tof_array = np.arange(original_tof_array[0], original_tof_array[-1], bin_value)
            new_tof_array = np.append(new_tof_array, new_tof_array[-1] + bin_value)

            linear_tof_bin_array = [[] for _ in np.arange(len(new_tof_array)-1)]
            for _tof_index, _bin in enumerate(original_tof_array):
                result = np.where(_bin >= new_tof_array)
                index = result[0][-1]
                linear_tof_bin_array[index].append(_tof_index)

            print(f"linear_tof_bin_array: {linear_tof_bin_array}")

            # array_of_bins = [[] for _ in np.arange(len(new_tof_array)-1)]
            # for _index, _bin in enumerate(linear_tof_bin_array[:-1]):
            #     array_of_bins[_index] = [linear_tof_bin_array[_index][0],
            #                              linear_tof_bin_array[_index+1][0]]
            # array_of_bins[-1] = [linear_tof_bin_array[-1][0],
            #                      linear_tof_bin_array[-1][-1] + 1]

        elif self.source_array == TimeSpectraKeys.lambda_array:
            original_lambda_array = np.array(self.parent.time_spectra[TimeSpectraKeys.lambda_array])
            new_lambda_array = np.arange(original_lambda_array[0], original_lambda_array[-1], bin_value)
            new_lambda_array = np.append(new_lambda_array, original_lambda_array[-1] + bin_value)

            linear_lambda_bin_array = [[] for _ in np.arange(len(new_lambda_array)-1)]
            for _tof_index, _bin in enumerate(original_lambda_array):
                result = np.where(_bin >= new_lambda_array)
                index = result[0][-1]
                linear_lambda_bin_array[index].append(_tof_index)

            print(f"linear_lambda_bin_array: {linear_lambda_bin_array}")

            # array_of_bins = [[] for _ in np.arange(len(new_lambda_array)-1)]
            # for _index, _bin in enumerate(linear_lambda_bin_array[:-1]):
            #     array_of_bins[_index] = [linear_lambda_bin_array[_index][0],
            #                              linear_lambda_bin_array[_index+1][0]]
            # array_of_bins[-1] = [linear_lambda_bin_array[-1][0],
            #                      linear_lambda_bin_array[-1][-1] + 1]

        # self.linear_bins[TimeSpectraKeys.file_index_array] = array_of_bins
        # self.logger.info(f"linear file index array of bins: {array_of_bins}")

    def create_linear_lambda_array(self, lambda_value):
        """this method create the linear lambda array"""
        original_lambda_array = np.array(self.parent.time_spectra[TimeSpectraKeys.lambda_array])
        linear_bins = self._create_general_linear_array(stepping=lambda_value,
                                                         original_array=original_lambda_array)
        self.linear_bins[TimeSpectraKeys.lambda_array] = linear_bins

    def _create_general_linear_array(self, stepping=None, original_array=None):
        """
        generic function used to create a linear bin array

        :param stepping: stepping bin value
        :param original_array: original array that will be used to determine when to stop
        :return: the linear bin array
        """
        left_value = original_array[0]
        right_value = stepping + left_value
        _linear_bins = []
        while right_value < original_array[-1]:
            _linear_bins.append(left_value)
            left_value = right_value
            right_value += stepping
        _linear_bins.append(right_value)
        return np.array(_linear_bins)

    def create_linear_bin_arrays(self):
        self.logger.info("Creating the other arrays")
        # if source_array == TimeSpectraKeys.file_index_array:
        file_index_array_of_bins = self.linear_bins[TimeSpectraKeys.file_index_array]

        original_tof_array = np.array(self.parent.time_spectra[TimeSpectraKeys.tof_array])
        original_lambda_array = np.array(self.parent.time_spectra[TimeSpectraKeys.lambda_array])

        lambda_array_of_bins = [[] for _ in np.arange(len(file_index_array_of_bins))]
        tof_array_of_bins = [[] for _ in np.arange(len(file_index_array_of_bins))]

        delta_tof = 0
        delta_lambda = 0

        for _index, _file_index_bin in enumerate(file_index_array_of_bins[:-1]):
            if _file_index_bin == []:
                tof_array_of_bins[_index] = []
                lambda_array_of_bins[_index] = []
            else:
                tof_array_of_bins[_index] = [original_tof_array[_file_index_bin[0]],
                                             original_tof_array[_file_index_bin[1]]]
                lambda_array_of_bins[_index] = [original_lambda_array[_file_index_bin[0]],
                                                original_lambda_array[_file_index_bin[1]]]

                if delta_tof == 0:
                    delta_tof = original_tof_array[_file_index_bin[1]] - original_tof_array[_file_index_bin[0]]
                    delta_lambda = original_lambda_array[_file_index_bin[1]] - original_lambda_array[
                        _file_index_bin[0]]

        tof_array_of_bins[-1] = [tof_array_of_bins[-2][1], tof_array_of_bins[-2][1] + delta_tof]
        lambda_array_of_bins[-1] = [lambda_array_of_bins[-2][1], lambda_array_of_bins[-2][1] + delta_lambda]

        self.linear_bins[TimeSpectraKeys.tof_array] = tof_array_of_bins
        self.linear_bins[TimeSpectraKeys.lambda_array]= lambda_array_of_bins

    # @staticmethod
    # def create_index_of_bins_in_original_array(bin_array=None, original_array=None):
    #     """
    #     This method determine the index of the various bin in the original array. This will then be
    #     used to find the equivalent location in the other arrays, for example lambda and file_index when
    #     the bin_array was calculated for tof
    #
    #     it may look like [[0],[],[],[1],[],[],[2,3]]
    #
    #     :param bin_array: bin array created (for example lambda_bin_array)
    #     :param original_array: original array (for example the original_lambda_array)
    #     :return: an array of the new bins with the file index position and in which bins they belong
    #     """
    #
    #     bins_with_index_of_file_index_in_it = [[] for _ in np.arange(len(bin_array))]
    #     for _file_index, _bin in enumerate(original_array):
    #         result = np.where(_bin >= bin_array)
    #         index = result[0][-1]
    #         bins_with_index_of_file_index_in_it[index].append(_file_index)
    #
    #     return bins_with_index_of_file_index_in_it
    #
    #     # index_of_bins_in_original_array = []
    #     # for _bin in bin_array:
    #     #     result = np.where(_bin <= original_array)
    #     #     try:
    #     #         index_of_bins_in_original_array.append(result[0][0])
    #     #     except IndexError:  # exception is value is outside of original range
    #     #         pass
    #     # return index_of_bins_in_original_array

    def get_linear_delta_file_index(self):
        return self._get_linear_delta(key=TimeSpectraKeys.file_index_array)

    def get_linear_delta_tof(self):
        return self._get_linear_delta(key=TimeSpectraKeys.tof_array)

    def get_linear_delta_lambda(self):
        return self._get_linear_delta(key=TimeSpectraKeys.lambda_array)

    def _get_linear_delta(self, key=TimeSpectraKeys.file_index_array):
        return self.linear_bins[key][0][1] - self.linear_bins[key][0][0]

    def get_linear_file_index(self):
        return self.linear_bins[TimeSpectraKeys.file_index_array]

    def get_linear_tof(self):
        return self.linear_bins[TimeSpectraKeys.tof_array]

    def get_linear_lambda(self):
        return self.linear_bins[TimeSpectraKeys.lambda_array]
