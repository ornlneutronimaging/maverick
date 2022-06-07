import numpy as np
import logging

from ..utilities import TimeSpectraKeys


class LogBin:

    log_bins = {TimeSpectraKeys.tof_array: None,
                TimeSpectraKeys.file_index_array: None,
                TimeSpectraKeys.lambda_array: None}

    def __init__(self, parent=None, source_radio_button=TimeSpectraKeys.file_index_array):
        self.parent = parent
        self.source_radio_button = source_radio_button
        self.logger = logging.getLogger("maverick")

    def create_log_file_index_bin_array(self, bin_value=1):
        """
        This method create the 1D array of the bin positions
        :param source_array: either 'file_index', 'lambda' or 'tof'
        :param bin_value: value of the logarithmic bin
        """
        original_array = np.array(self.parent.time_spectra[self.source_radio_button])
        if self.source_radio_button == TimeSpectraKeys.file_index_array:
            pass

        elif self.source_radio_button == TimeSpectraKeys.tof_array:
            pass

        elif self.source_radio_button == TimeSpectraKeys.lambda_array:
            pass

        else:
            raise NotImplementedError(f"method {self.source_radio_button} not implemented!")

        # create the log bin array [value1, value2, value3, value4....]
        start_parameter = original_array[0]
        parameter_end = original_array[-1]
        new_bin_array = [start_parameter]
        parameter = start_parameter
        while parameter <= parameter_end:
            parameter += parameter * bin_value
            new_bin_array.append(parameter)

        # in case the last bin is smaller than the last array value
        if new_bin_array[-1] <= original_array[-1]:
            parameter += parameter * bin_value
            new_bin_array.append(parameter)

        # we need to find where the file index end up in this array
        # will create [[0],[],[],[1],[2,3],[4,5,6,7],...]
        index_of_bin = [[] for _ in np.arange(len(new_bin_array)-1)]
        for _bin_index, _bin in enumerate(original_array):

            result = np.where(_bin >= new_bin_array)
            try:
                index = result[0][-1]
                index_of_bin[index].append(_bin_index)
            except IndexError:
                continue

        # remove empty bins
        clean_index_of_bins = [_bin for _bin in index_of_bin if _bin != []]
        self.logger.info(f"index of files in bins: {clean_index_of_bins}")

        # # create the array of bins [[left_bin,right_bin],[left_bin,right_bin]..]
        # array_of_bins = [[] for _ in np.arange(len(bin_array)-1)]
        # for _index, _bin in enumerate(bin_array[:-1]):
        #     array_of_bins[_index] = [bin_array[_index], bin_array[+1]]
        #
        # # self.log_bins[self.source_radio_button] = bin_array
        # self.logger.info(f"log {self.source_radio_button} array of bins: {bin_array}")
        # self.log_bins[self.source_radio_button] = array_of_bins

    def create_log_bin_arrays(self):
        array_of_bins = self.log_bins[self.source_radio_button]

        if self.source_radio_button == TimeSpectraKeys.tof_array:

            file_index_array_of_bins = [[] for _ in np.arange(len(array_of_bins))]
            lambda_array_of_bins = [[] for _ in np.arange(len(array_of_bins))]




        pass

    def get_log_file_index(self):
        return self.log_bins[TimeSpectraKeys.file_index_array]

    def get_log_tof(self):
        return self.log_bins[TimeSpectraKeys.tof_array]

    def get_log_lambda(self):
        return self.log_bins[TimeSpectraKeys.lambda_array]