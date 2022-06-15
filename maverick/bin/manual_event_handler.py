import logging
import pyqtgraph as pg
from qtpy.QtWidgets import QMenu
from qtpy import QtGui
import numpy as np

from ..utilities import TimeSpectraKeys
from .plot import Plot
from ..utilities.get import Get
from . import TO_MICROS_UNITS, TO_ANGSTROMS_UNITS
from ..utilities.table_handler import TableHandler
from ..utilities.math_tools import get_value_of_closest_match

FILE_INDEX_BIN_MARGIN = 0.5
UNSELECTED_BIN = (0, 0, 200, 50)
SELECTED_BIN = (0, 200, 0, 50)


class ManualEventHandler:

    def __init__(self, parent=None):
        self.parent = parent
        self.logger = logging.getLogger('maverick')

        self.tof_bin_margin = (self.parent.time_spectra[TimeSpectraKeys.tof_array][1] -
                               self.parent.time_spectra[TimeSpectraKeys.tof_array][0]) / 2.

        self.lambda_bin_margin = (self.parent.time_spectra[TimeSpectraKeys.lambda_array][1] -
                                  self.parent.time_spectra[TimeSpectraKeys.lambda_array][0]) / 2

    def refresh_manual_tab(self):
        """refresh the right plot with profile + bin selected when the manual tab is selected"""
        o_plot = Plot(parent=self.parent)
        o_plot.refresh_profile_plot()

    def add_bin(self):

        o_get = Get(parent=self.parent)
        time_spectra_x_axis_name = o_get.bin_x_axis_selected()
        x_axis = self.parent.time_spectra[time_spectra_x_axis_name]

        o_table = TableHandler(table_ui=self.parent.ui.bin_manual_tableWidget)
        last_row = o_table.row_count()

        if time_spectra_x_axis_name == TimeSpectraKeys.file_index_array:
            default_bin = [x_axis[0] - FILE_INDEX_BIN_MARGIN,
                           x_axis[0] + FILE_INDEX_BIN_MARGIN]
        elif time_spectra_x_axis_name == TimeSpectraKeys.tof_array:
            default_bin = [x_axis[0] - self.tof_bin_margin,
                           x_axis[0] + self.tof_bin_margin]
            default_bin = [_value * TO_MICROS_UNITS for _value in default_bin]
        else:
            default_bin = [x_axis[0] - self.lambda_bin_margin,
                           x_axis[1] + self.lambda_bin_margin]
            default_bin = [_value * TO_ANGSTROMS_UNITS for _value in default_bin]

        item = pg.LinearRegionItem(values=default_bin,
                                   orientation='vertical',
                                   brush=SELECTED_BIN,
                                   movable=True,
                                   bounds=None)
        item.setZValue(-10)
        item.sigRegionChangeFinished.connect(self.parent.bin_manual_region_changed)

        self.parent.bin_profile_view.addItem(item)
        # dict_of_bins_item[last_row] = item
        # self.parent.dict_of_bins_item = dict_of_bins_item
        self.parent.list_of_manual_bins_item.append(item)

        # add new entry in table
        o_table.insert_empty_row(last_row)

        o_table.insert_item(row=last_row,
                            column=0,
                            value=f"{last_row}",
                            editable=False)

        _file_index = self.parent.time_spectra[TimeSpectraKeys.file_index_array][0]
        o_table.insert_item(row=last_row,
                            column=1,
                            value=_file_index,
                            editable=False)

        _tof = self.parent.time_spectra[TimeSpectraKeys.tof_array][0] * TO_MICROS_UNITS
        o_table.insert_item(row=last_row,
                            column=2,
                            value=_tof,
                            format_str="{:.2f}",
                            editable=False)

        _lambda = self.parent.time_spectra[TimeSpectraKeys.lambda_array][0] * TO_ANGSTROMS_UNITS
        o_table.insert_item(row=last_row,
                            column=3,
                            value=_lambda,
                            format_str="{:.3f}",
                            editable=False)

    def populate_table_with_auto_mode(self):
        o_get = Get(parent=self.parent)
        bins = o_get.auto_bins_currently_activated()

        o_table = TableHandler(table_ui=self.parent.ui.bin_manual_tableWidget)
        o_table.remove_all_rows()

        file_index_array = bins[TimeSpectraKeys.file_index_array]
        tof_array = bins[TimeSpectraKeys.tof_array]
        lambda_array = bins[TimeSpectraKeys.lambda_array]

        self.parent.list_of_manual_bins_item = []

        _row = 0
        for _index, _bin in enumerate(file_index_array):

            if _bin == []:
                continue

            o_table.insert_empty_row(_row)

            o_table.insert_item(row=_row,
                                column=0,
                                value=f"{_row}",
                                editable=False)

            _file_index = _bin
            _file_index_formatted = ManualEventHandler.format_str(_file_index,
                                                                  format_str="{:d}",
                                                                  factor=1,
                                                                  data_type=TimeSpectraKeys.file_index_array)
            o_table.insert_item(row=_row,
                                column=1,
                                format_str=_file_index_formatted,
                                editable=False)

            _tof = tof_array[_index]
            _tof_formatted = ManualEventHandler.format_str(_tof,
                                                           format_str="{:.2f}",
                                                           factor=TO_MICROS_UNITS,
                                                           data_type=TimeSpectraKeys.tof_array)

            o_table.insert_item(row=_row,
                                column=2,
                                format_str=_tof_formatted,
                                editable=False)

            _lambda = lambda_array[_index]
            _lambda_formatted = ManualEventHandler.format_str(_lambda,
                                                              format_str="{:.3f}",
                                                              factor=TO_ANGSTROMS_UNITS,
                                                              data_type=TimeSpectraKeys.lambda_array)
            o_table.insert_item(row=_row,
                                column=3,
                                format_str=_lambda_formatted,
                                editable=False)

            item = self.add_bin_in_plot(row=_row,
                                        file_index_bin=_bin,
                                        tof_bin=_tof,
                                        lambda_bin=_lambda)

            self.parent.list_of_manual_bins_item.append(item)

            _row += 1

        o_table.select_rows([0])

    def add_bin_in_plot(self, row=0, file_index_bin=None, tof_bin=None, lambda_bin=None):
        o_get = Get(parent=self.parent)
        current_x_axis = o_get.bin_x_axis_selected()
        if current_x_axis == TimeSpectraKeys.file_index_array:
            bin = file_index_bin
            bin_size = [bin[0] - FILE_INDEX_BIN_MARGIN,
                        bin[-1] + FILE_INDEX_BIN_MARGIN]
        elif current_x_axis == TimeSpectraKeys.tof_array:
            bin = tof_bin
            bin_size = [bin[0] - self.tof_bin_margin,
                        bin[-1] + self.tof_bin_margin]
        elif current_x_axis == TimeSpectraKeys.lambda_array:
            bin = lambda_bin
            bin_size = [bin[0] - self.lambda_bin_margin,
                        bin[1] + self.lambda_bin_margin]
        else:
            raise NotImplementedError("x_axis not implemented!")

        if row == 0:
            brush_selection = SELECTED_BIN
        else:
            brush_selection = UNSELECTED_BIN

        item = pg.LinearRegionItem(values=bin_size,
                                   orientation='vertical',
                                   brush=brush_selection,
                                   movable=True,
                                   bounds=None)
        item.setZValue(-10)
        item.sigRegionChangeFinished.connect(self.parent.bin_manual_region_changed)
        self.parent.bin_profile_view.addItem(item)

        return item

    def manual_table_right_click(self):
        o_table = TableHandler(table_ui=self.parent.ui.bin_manual_tableWidget)
        last_row = o_table.row_count()
        if last_row == 0:  # no entry in the table
            return

        row_selected = o_table.get_row_selected()
        if row_selected == -1:  # no row selected, exit
            return

        menu = QMenu(self.parent)

        remove_bin = menu.addAction("Remove selected bin")

        action = menu.exec_(QtGui.QCursor.pos())
        if action == remove_bin:
            self.remove_selected_bin()
        else:
            pass

    def remove_selected_bin(self):
        """
        remove from the manual table the bin selected
        """
        o_table = TableHandler(table_ui=self.parent.ui.bin_manual_tableWidget)
        row_selected = o_table.get_row_selected()
        item_to_remove = self.parent.list_of_manual_bins_item[row_selected]
        self.parent.bin_profile_view.removeItem(item_to_remove)
        self.parent.list_of_manual_bins_item.pop(row_selected)
        o_table.remove_row(row=row_selected)
        self.logger.info(f"User manually removed row: {row_selected}")

    def bin_manually_moved(self, item_id=None):
        self.bin_manually_moving(item_id=item_id)

        # 1. using region selected threshold, and the current axis, find the snapping left and right indexes
        #    and save them into a manual_snapping_indexes_bins = {0: [0, 3], 1: [1, 10], ..}
        self.record_snapping_indexes_bin()

        # 2. reposition the clean bins into the plot
        self.update_items_displayed()

        # 3. using those indexes create the ranges for each bins and for each time axis and save those in
        #    self.parent.manual_bins['file_index_array': {0: [0, 1, 2, 3], 1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], ...},...}
        self.create_all_ranges()

        # 4. update table
        self.update_table()

    def bin_manually_moving(self, item_id=None):
        o_get = Get(parent=self.parent)
        working_row = o_get.manual_working_row(working_item_id=item_id)
        self.select_working_row(working_row=working_row)

    def select_working_row(self, working_row=0):
        o_table = TableHandler(table_ui=self.parent.ui.bin_manual_tableWidget)
        o_table.select_rows(list_of_rows=[working_row])

    def update_table(self):

        o_table = TableHandler(table_ui=self.parent.ui.bin_manual_tableWidget)

        file_index_array = self.parent.manual_bins[TimeSpectraKeys.file_index_array]
        tof_array = self.parent.manual_bins[TimeSpectraKeys.tof_array]
        lambda_array = self.parent.manual_bins[TimeSpectraKeys.lambda_array]

        for _row in file_index_array.keys():
            list_runs = file_index_array[_row]
            list_runs_formatted = ManualEventHandler.format_str(list_runs,
                                                                format_str="{:d}",
                                                                factor=1,
                                                                data_type=TimeSpectraKeys.file_index_array)
            o_table.set_item_with_str(row=_row, column=1, cell_str=list_runs_formatted)

            list_tof = tof_array[_row]
            list_tof_formatted = ManualEventHandler.format_str(list_tof,
                                                               format_str="{:.2f}",
                                                               factor=TO_MICROS_UNITS,
                                                               data_type=TimeSpectraKeys.tof_array)
            o_table.set_item_with_str(row=_row, column=2, cell_str=list_tof_formatted)

            list_lambda = lambda_array[_row]
            list_lambda_formatted = ManualEventHandler.format_str(list_lambda,
                                                                  format_str="{:.3f}",
                                                                  factor=TO_ANGSTROMS_UNITS,
                                                                  data_type=TimeSpectraKeys.lambda_array)
            o_table.set_item_with_str(row=_row, column=3, cell_str=list_lambda_formatted)

    def create_all_ranges(self):
        manual_snapping_indexes_bins = self.parent.manual_snapping_indexes_bins

        file_index_array = {}
        tof_array = {}
        lambda_array = {}

        for _bin in manual_snapping_indexes_bins.keys():
            left_index, right_index = manual_snapping_indexes_bins[_bin]

            # tof_array
            bins_file_index_array = self.parent.time_spectra[TimeSpectraKeys.file_index_array]
            bins_file_index_range = bins_file_index_array[left_index: right_index + 1]
            file_index_array[_bin] = bins_file_index_range

            # tof_array
            bins_tof_array = self.parent.time_spectra[TimeSpectraKeys.tof_array]
            bins_tof_range = bins_tof_array[left_index: right_index + 1]
            tof_array[_bin] = bins_tof_range

            # lambda_array
            bins_lambda_array = self.parent.time_spectra[TimeSpectraKeys.lambda_array]
            bins_lambda_range = bins_lambda_array[left_index: right_index + 1]
            lambda_array[_bin] = bins_lambda_range

        self.parent.manual_bins[TimeSpectraKeys.file_index_array] = file_index_array
        self.parent.manual_bins[TimeSpectraKeys.tof_array] = tof_array
        self.parent.manual_bins[TimeSpectraKeys.lambda_array] = lambda_array

    def update_items_displayed(self):
        """
        this will remove the old item and put the new one with the edges snap to the x-axis
        """
        o_get = Get(parent=self.parent)
        x_axis_type_selected = o_get.bin_x_axis_selected()
        x_axis = self.parent.time_spectra[x_axis_type_selected]

        manual_snapping_indexes_bins = self.parent.manual_snapping_indexes_bins

        margin = self.margin()

        list_of_manual_bins_item = []
        for _row in manual_snapping_indexes_bins.keys():
            left_value_checked, right_value_checked = manual_snapping_indexes_bins[_row]
            left_value_checked = x_axis[left_value_checked] - margin
            right_value_checked = x_axis[right_value_checked] + margin

            _item = self.parent.list_of_manual_bins_item[_row]
            self.parent.bin_profile_view.removeItem(_item)

            item = pg.LinearRegionItem(values=[left_value_checked, right_value_checked],
                                       orientation='vertical',
                                       brush=SELECTED_BIN,
                                       movable=True,
                                       bounds=None)
            item.setZValue(-10)
            item.sigRegionChangeFinished.connect(self.parent.bin_manual_region_changed)
            item.sigRegionChanged.connect(self.parent.bin_manual_region_changing)
            self.parent.bin_profile_view.addItem(item)
            list_of_manual_bins_item.append(item)

        self.parent.list_of_manual_bins_item = list_of_manual_bins_item

    def record_bin_ranges(self):
        """
        record all the bins ranges in all the x-axis values
        """
        pass

    def record_snapping_indexes_bin(self):
        """
        This will check each bin from the manual table and move, if necessary, any of the edges
        to snap to the closet x axis values
        """
        manual_snapping_indexes_bins = {}
        for _row, _item in enumerate(self.parent.list_of_manual_bins_item):
            [left, right] = _item.getRegion()

            # bring left and right to closest correct values
            left_value_checked, right_value_checked = self.checked_range(left=left, right=right)
            manual_snapping_indexes_bins[_row] = [left_value_checked, right_value_checked]

        self.parent.manual_snapping_indexes_bins = manual_snapping_indexes_bins

    def margin(self, axis_type=TimeSpectraKeys.file_index_array):
        if axis_type == TimeSpectraKeys.file_index_array:
            return FILE_INDEX_BIN_MARGIN
        elif axis_type == TimeSpectraKeys.tof_array:
            return self.tof_bin_margin
        elif axis_type == TimeSpectraKeys.lambda_array:
            return self.lambda_bin_margin
        else:
            raise NotImplementedError(f"axis type {axis_type} not implemented!")

    def checked_range(self, left=0, right=0):
        """this method makes sure that the left and right values stay within the maximum range of the data
        for the current axis selected"""
        o_get = Get(parent=self.parent)
        x_axis_type_selected = o_get.bin_x_axis_selected()
        x_axis = self.parent.time_spectra[x_axis_type_selected]

        if left < x_axis[0]:
            left = x_axis[0]

        if right >= x_axis[-1]:
            right = x_axis[-1]

        index_clean_left_value = get_value_of_closest_match(array_to_look_for=x_axis,
                                                      value=left,
                                                      left_margin=True)
        index_clean_right_value = get_value_of_closest_match(array_to_look_for=x_axis,
                                                       value=right,
                                                       left_margin=False)

        clean_left_value = x_axis[index_clean_left_value]
        if clean_left_value < left:
            clean_left_value = x_axis[index_clean_left_value + 1]

        clean_right_value = x_axis[index_clean_right_value]
        if clean_right_value > right:
            clean_right_value = x_axis[index_clean_right_value - 1]

        print(f"left: {left} and clean_left_value:{clean_left_value}")

        return clean_left_value, clean_right_value

    @staticmethod
    def format_str(input_list, format_str="{}", factor=1, data_type=TimeSpectraKeys.file_index_array):
        """
        format the list of file_index, tof or lambda to fill the manual bin table
        :param input_list:
        :param format_str:
        :param factor:
        :param data_type:
        :return:
        """
        if data_type == TimeSpectraKeys.file_index_array:
            if len(input_list) == 1:
                return format_str.format(input_list[0] * factor)
            elif len(input_list) == 2:
                return format_str.format(input_list[0] * factor) + ", " + \
                       format_str.format(input_list[1] * factor)
            else:
                return format_str.format(input_list[0] * factor) + " ... " + \
                       format_str.format(input_list[-1] * factor)
        else:
            if len(input_list) == 1:
                return format_str.format(input_list[0] * factor)
            else:
                return format_str.format(input_list[0] * factor) + " ... " + \
                       format_str.format(input_list[-1] * factor)
