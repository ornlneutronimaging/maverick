import numpy as np
import logging

from ..utilities import TimeSpectraKeys


class LogBin:

    log_bins = {TimeSpectraKeys.tof_array: None,
                TimeSpectraKeys.file_index_array: None,
                TimeSpectraKeys.lambda_array: None}

    def __init__(self, parent=None):
        self.parent = parent
        self.logger = logging.getLogger("maverick")

    def create_linear_file_index_bin_array(self, source_array=TimeSpectraKeys.tof_array,
                                           bin_value=1):

        original_array = np.array(self.parent.time_spectra[source_array])
        if source_array == TimeSpectraKeys.file_index_array:
            pass
        elif source_array == TimeSpectraKeys.tof_array:
            t0 = original_array[0]
            t_end = original_array[-1]
            bin_array = []
            t = t0
            while t <= t_end:
                t += t * bin_value
                bin_array.append(t)

        elif source_array == TimeSpectraKeys.lambda_array:
            pass
        else:
            raise NotImplementedError(f"method {source_array} not implemented!")

        self.log_bins[source_array] = bin_array
        self.logger.info(f"log {source_array} array of bins: {bin_array}")

    def get_log_file_index(self):
        return self.log_bins[TimeSpectraKeys.file_index_array]

    def get_log_tof(self):
        return self.log_bins[TimeSpectraKeys.tof_array]

    def get_log_lambda(self):
        return self.log_bins[TimeSpectraKeys.lambda_array]