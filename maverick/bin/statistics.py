from ..utilities.get import Get

from ..utilities import BinMode, BinAutoMode, TimeSpectraKeys
from ..utilities.string import format_str
from ..utilities.table_handler import TableHandler

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

            _row += 1
