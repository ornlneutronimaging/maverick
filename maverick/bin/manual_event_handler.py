import logging
import pyqtgraph as pg
from qtpy.QtWidgets import QMenu
from qtpy import QtGui

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
        pass

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

    def bin_manually_moved(self):

        list_of_manual_bins_item = []
        for _row, _item in enumerate(self.parent.list_of_manual_bins_item):
            [left, right] = _item.getRegion()

            # bring left and right to closest correct values
            left_checked, right_checked = self.checked_range(left=left,
                                                             right=right)

            self.parent.bin_profile_view.removeItem(_item)

            item = pg.LinearRegionItem(values=[left_checked, right_checked],
                                       orientation='vertical',
                                       brush=SELECTED_BIN,
                                       movable=True,
                                       bounds=None)
            item.setZValue(-10)
            item.sigRegionChangeFinished.connect(self.parent.bin_manual_region_changed)
            self.parent.bin_profile_view.addItem(item)
            list_of_manual_bins_item.append(item)

        self.parent.list_of_manual_bins_item = list_of_manual_bins_item

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

        margin = self.margin(axis_type=x_axis_type_selected)

        if left < x_axis[0] - margin:
            left = x_axis[0] - margin

        if right >= x_axis[-1] + margin:
            right = x_axis[-1] + margin

        clean_left = get_value_of_closest_match(array_to_look_for=x_axis, value=left, left_margin=True)
        clean_right = get_value_of_closest_match(array_to_look_for=x_axis, value=right, left_margin=False)

        return clean_left - margin, clean_right + margin
