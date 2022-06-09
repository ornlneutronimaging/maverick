import logging
import pyqtgraph as pg

from ..utilities import TimeSpectraKeys
from .plot import Plot
from ..utilities.get import Get
from . import TO_MICROS_UNITS, TO_ANGSTROMS_UNITS
from ..utilities.table_handler import TableHandler

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

        dict_of_bins_item = {}
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
        self.parent.bin_profile_view.addItem(item)
        dict_of_bins_item[last_row] = item

        self.parent.dict_of_bins_item = dict_of_bins_item
