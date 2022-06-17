import numpy as np

from ..utilities.get import Get
from ..utilities import BinMode, BinAutoMode, TimeSpectraKeys, BinAlgorithm
from ..utilities.string import format_str
from ..utilities.table_handler import TableHandler
from ..session import SessionKeys

from . import TO_MICROS_UNITS, TO_ANGSTROMS_UNITS


class Statistics:

    def __init__(self, parent=None):
        self.parent = parent

    def update(self):

        o_get = Get(parent=self.parent)

        # check if we are looking for the auto or the manual bins
        bin_mode = o_get.bin_mode()

        if bin_mode == BinMode.auto:

            bin_auto_mode = o_get.bin_auto_mode()
            if bin_auto_mode == BinAutoMode.linear:
                list_bins = self.parent.linear_bins
            else:
                list_bins = self.parent.log_bins

        else:

            list_bins = self.parent.manual_bins

        # if no bins to display, stop here
        if list_bins[TimeSpectraKeys.file_index_array] is None:
            return

        o_table = TableHandler(table_ui=self.parent.ui.statistics_tableWidget)
        o_table.remove_all_rows()

        file_index_bins = list_bins[TimeSpectraKeys.file_index_array]
        tof_bins = list_bins[TimeSpectraKeys.tof_array]
        lambda_bins = list_bins[TimeSpectraKeys.lambda_array]

        _row = 0
        for _bin_index, _bin in enumerate(file_index_bins):

            if _bin == []:
                continue

            o_table.insert_empty_row(row=_row)

            o_table.insert_item(row=_row,
                                column=0,
                                value=str(_row),
                                editable=False)

            list_runs = file_index_bins[_bin_index]
            list_runs_formatted = format_str(list_runs,
                                             format_str="{:d}",
                                             factor=1,
                                             data_type=TimeSpectraKeys.file_index_array)
            o_table.insert_item(row=_row,
                                column=1,
                                value=list_runs_formatted,
                                editable=False)

            list_tof = tof_bins[_bin_index]
            list_tof_formatted = format_str(list_tof,
                                            format_str="{:.2f}",
                                            factor=TO_MICROS_UNITS,
                                            data_type=TimeSpectraKeys.tof_array)
            o_table.insert_item(row=_row,
                                column=2,
                                value=list_tof_formatted,
                                editable=False)

            list_lambda = lambda_bins[_bin_index]
            list_lambda_formatted = format_str(list_lambda,
                                               format_str="{:.3f}",
                                               factor=TO_ANGSTROMS_UNITS,
                                               data_type=TimeSpectraKeys.lambda_array)
            o_table.insert_item(row=_row,
                                column=3,
                                value=list_lambda_formatted,
                                editable=False)

            # calculate statistics
            _data_dict = self.extract_data_for_this_bin(list_runs=list_runs)

            full_image = _data_dict['full_image']
            roi_of_image = _data_dict['roi_of_image']

            # mean
            full_mean = np.mean(full_image)
            roi_mean = np.mean(roi_of_image)
            str_mean = f"{full_mean:.3f} ({roi_mean:.3f})"
            o_table.insert_item(row=_row,
                                column=4,
                                value=str_mean,
                                editable=False)

            # median
            full_median = np.median(full_image)
            roi_median = np.median(roi_of_image)
            str_median = f"{full_median:.3f} ({roi_median:.3f})"
            o_table.insert_item(row=_row,
                                column=5,
                                value=str_median,
                                editable=False)

            # std
            full_std = np.std(full_image)
            roi_std = np.std(roi_of_image)
            str_std = f"{full_std:.3f} ({roi_std:.3f})"
            o_table.insert_item(row=_row,
                                column=6,
                                value=str_std,
                                editable=False)

            # min
            full_min = np.min(full_image)
            roi_min = np.min(roi_of_image)
            str_min = f"{full_min:.3f} ({roi_min:.3f})"
            o_table.insert_item(row=_row,
                                column=7,
                                value=str_min,
                                editable=False)

            # max
            full_max = np.max(full_image)
            roi_max = np.max(roi_of_image)
            str_max = f"{full_max:.3f} ({roi_max:.3f})"
            o_table.insert_item(row=_row,
                                column=8,
                                value=str_max,
                                editable=False)

            _row += 1

    def extract_data_for_this_bin(self, list_runs=None):
        """
        this method isolate the data of only the runs of the corresponding runs, and only for the ROI selected

        :param list_runs:
        :return:
        """
        # retrieve statistics
        [x0, y0, width, height] = self.parent.session[SessionKeys.combine_roi]

        data_to_work_with = []
        for _run_index in list_runs:
            data_to_work_with.append(self.parent.combine_data[_run_index])

        region_to_work_with = [_data[y0: y0+height, x0: x0+width] for _data in data_to_work_with]

        # how to add images
        o_get = Get(parent=self.parent)
        bin_method = o_get.bin_add_method()
        if bin_method == BinAlgorithm.mean:
            full_image_to_work_with = np.mean(data_to_work_with, axis=0)
            roi_image_to_work_with = np.mean(region_to_work_with, axis=0)
        elif bin_method == BinAlgorithm.median:
            full_image_to_work_with = np.median(data_to_work_with, axis=0)
            roi_image_to_work_with = np.median(region_to_work_with, axis=0)
        else:
            raise NotImplementedError("this method of adding the binned images is not suppported!")

        return {'full_image': full_image_to_work_with,
                'roi_of_image': roi_image_to_work_with}

    def plot_statistics(self):
        pass
