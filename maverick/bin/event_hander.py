import copy
import logging
import numpy as np
import pyqtgraph as pg

from ..session import SessionKeys
from ..utilities import BinMode
from ..utilities.get import Get
from ..utilities import TimeSpectraKeys, BinAutoMode
from .. import LAMBDA, MICRO, ANGSTROMS
from .linear_bin import LinearBin
from .log_bin import LogBin
from ..utilities.table_handler import TableHandler
from ..utilities.status_message_config import StatusMessageStatus, show_status_message

FILE_INDEX_BIN_MARGIN = 0.5
TO_MICROS_UNITS = 1e6
TO_ANGSTROMS_UNITS = 1e10

class EventHandler:

    tof_bin_margin = 0
    lambda_bin_margin = 0

    def __init__(self, parent=None):
        self.parent = parent
        self.logger = logging.getLogger('maverick')

        self.tof_bin_margin = (self.parent.time_spectra[TimeSpectraKeys.tof_array][1] -
                               self.parent.time_spectra[TimeSpectraKeys.tof_array][0]) / 2.

        self.lambda_bin_margin = (self.parent.time_spectra[TimeSpectraKeys.lambda_array][1] -
                                  self.parent.time_spectra[TimeSpectraKeys.lambda_array][0]) / 2

    def refresh_tab(self):
        # refresh profile using right x_axis

        self.parent.bin_profile_view.clear()  # clear previous plot
        if not (self.parent.list_bins_items is None):  # remove previous bins
            for _item in self.parent.list_bins_items:
                self.parent.bin_profile_view.removeItem(_item)

        profile_signal = self.parent.profile_signal

        o_get = Get(parent=self.parent)
        combine_algorithm = o_get.combine_algorithm()
        time_spectra_x_axis_name = o_get.bin_x_axis_selected()

        x_axis = copy.deepcopy(self.parent.time_spectra[time_spectra_x_axis_name])

        if time_spectra_x_axis_name == TimeSpectraKeys.file_index_array:
            x_axis_label = "file index"
        elif time_spectra_x_axis_name == TimeSpectraKeys.tof_array:
            x_axis *= TO_MICROS_UNITS    # to display axis in micros
            x_axis_label = "tof (" + MICRO + "s)"
        elif time_spectra_x_axis_name == TimeSpectraKeys.lambda_array:
            x_axis *= TO_ANGSTROMS_UNITS    # to display axis in Angstroms
            x_axis_label = LAMBDA + "(" + ANGSTROMS + ")"

        self.parent.bin_profile_view.plot(x_axis, profile_signal, pen='r', symbol='x')
        self.parent.bin_profile_view.setLabel("left", f"{combine_algorithm} counts")
        self.parent.bin_profile_view.setLabel("bottom", x_axis_label)

        if o_get.bin_auto_mode() == BinAutoMode.linear:
            bins = self.parent.linear_bins[time_spectra_x_axis_name]
        else:
            bins = self.parent.log_bins[time_spectra_x_axis_name]

        list_item = []
        for _bin in bins:

            if _bin == []:
                continue

            if time_spectra_x_axis_name == TimeSpectraKeys.file_index_array:

                scale_bin = [_bin[0] - FILE_INDEX_BIN_MARGIN,
                             _bin[-1] + FILE_INDEX_BIN_MARGIN]

            elif time_spectra_x_axis_name == TimeSpectraKeys.tof_array:

                scale_bin = [_bin[0] - self.tof_bin_margin,
                             _bin[-1] + self.tof_bin_margin]
                scale_bin = [_value * TO_MICROS_UNITS for _value in scale_bin]

            else:

                scale_bin = [_bin[0] - self.lambda_bin_margin,
                             _bin[-1] + self.lambda_bin_margin]
                scale_bin = [_value * TO_ANGSTROMS_UNITS for _value in scale_bin]

            item = pg.LinearRegionItem(values=scale_bin,
                                       orientation='vertical',
                                       brush=None,
                                       movable=False,
                                       bounds=None)
            item.setZValue(-10)
            self.parent.bin_profile_view.addItem(item)
            list_item.append(item)

        self.parent.list_bins_items = list_item

    def bin_auto_radioButton_clicked(self):
        state_auto = self.parent.ui.auto_log_radioButton.isChecked()
        self.parent.ui.auto_linear_radioButton.setChecked(state_auto)
        self.parent.ui.auto_linear_radioButton.setChecked(not state_auto)
        self.parent.ui.bin_auto_log_frame.setEnabled(state_auto)
        self.parent.ui.bin_auto_linear_frame.setEnabled(not state_auto)
        o_get = Get(parent=self.parent)
        if o_get.bin_auto_mode() == BinAutoMode.log:
            self.auto_log_radioButton_changed()
        else:
            self.auto_linear_radioButton_changed()

    def bin_auto_manual_tab_changed(self, new_tab_index=0):
        if new_tab_index == 0:
            self.parent.session[SessionKeys.bin_mode] = BinMode.auto
        elif new_tab_index == 1:
            self.parent.session[SessionKeys.bin_mode] = BinMode.manual
        else:
            raise NotImplementedError("LinearBin mode not implemented!")

    def bin_auto_log_changed(self, source_radio_button=TimeSpectraKeys.file_index_array):
        self.logger.info(f"bin auto log changed: radio button changed -> {source_radio_button}")
        o_bin = LogBin(parent=self.parent,
                       source_radio_button=source_radio_button)

        self.parent.ui.auto_log_file_index_spinBox.blockSignals(True)
        self.parent.ui.auto_log_tof_doubleSpinBox.blockSignals(True)
        self.parent.ui.auto_log_lambda_doubleSpinBox.blockSignals(True)

        self.logger.info(f"-> original raw_file_index_array_binned:"
                         f" {self.parent.time_spectra[TimeSpectraKeys.file_index_array]}")
        self.logger.info(f"-> original raw_tof_array_binned: {self.parent.time_spectra[TimeSpectraKeys.tof_array]}")
        self.logger.info(f"-> original raw_lambda_array_binned:"
                         f" {self.parent.time_spectra[TimeSpectraKeys.lambda_array]}")

        o_get = Get(parent=self.parent)
        log_bin_requested = o_get.auto_log_bin_requested()
        self.logger.info(f"--> bin requested: {log_bin_requested}")

        if source_radio_button == TimeSpectraKeys.file_index_array:
            o_bin.create_log_file_index_bin_array(bin_value=log_bin_requested)

        elif source_radio_button == TimeSpectraKeys.tof_array:
            o_bin.create_log_file_index_bin_array(bin_value=log_bin_requested)
            o_bin.create_log_bin_arrays()

        elif source_radio_button == TimeSpectraKeys.lambda_array:
            o_bin.create_log_file_index_bin_array(bin_value=log_bin_requested)
            o_bin.create_log_bin_arrays()

        else:
            raise NotImplementedError("bin auto log algorithm not implemented!")

        self.logger.info(f"-> file_index_array_binned: {o_bin.log_bins[TimeSpectraKeys.file_index_array]}")
        self.logger.info(f"-> tof_array_binned: {o_bin.log_bins[TimeSpectraKeys.tof_array]}")
        self.logger.info(f"-> lambda_array_binned: {o_bin.log_bins[TimeSpectraKeys.lambda_array]}")

        self.parent.log_bins = {TimeSpectraKeys.file_index_array: o_bin.get_log_file_index(),
                                TimeSpectraKeys.tof_array: o_bin.get_log_tof(),
                                TimeSpectraKeys.lambda_array: o_bin.get_log_lambda()}

        self.fill_auto_table()
        self.refresh_tab()

        self.parent.ui.auto_log_file_index_spinBox.blockSignals(False)
        self.parent.ui.auto_log_tof_doubleSpinBox.blockSignals(False)
        self.parent.ui.auto_log_lambda_doubleSpinBox.blockSignals(False)

    def bin_auto_linear_changed(self, source_radio_button=TimeSpectraKeys.file_index_array):
        self.logger.info(f"bin auto linear changed: radio button changed -> {source_radio_button}")
        o_bin = LinearBin(parent=self.parent,
                          source_array=source_radio_button)
        self.parent.ui.auto_linear_file_index_spinBox.blockSignals(True)
        self.parent.ui.auto_linear_tof_doubleSpinBox.blockSignals(True)
        self.parent.ui.auto_linear_lambda_doubleSpinBox.blockSignals(True)

        self.logger.info(f"-> raw_file_index_array_binned: {self.parent.time_spectra[TimeSpectraKeys.file_index_array]}")
        self.logger.info(f"-> raw_tof_array_binned: {self.parent.time_spectra[TimeSpectraKeys.tof_array]}")
        self.logger.info(f"-> raw_lambda_array_binned: {self.parent.time_spectra[TimeSpectraKeys.lambda_array]}")

        if source_radio_button == TimeSpectraKeys.file_index_array:
            file_index_value = self.parent.ui.auto_linear_file_index_spinBox.value()
            self.logger.info(f"--> bin requested: {file_index_value}")
            o_bin.create_linear_file_index_bin_array(bin_value=file_index_value)
            o_bin.create_linear_bin_arrays()

        elif source_radio_button == TimeSpectraKeys.tof_array:
            tof_value = self.parent.ui.auto_linear_tof_doubleSpinBox.value()
            self.logger.info(f"--> bin requested: {tof_value}")
            o_bin.create_linear_file_index_bin_array(bin_value=tof_value * 1e-6)   # to switch to seconds
            o_bin.create_linear_bin_arrays()

        elif source_radio_button == TimeSpectraKeys.lambda_array:
            lambda_value = self.parent.ui.auto_linear_lambda_doubleSpinBox.value()
            self.logger.info(f"--> bin requested: {lambda_value}")
            o_bin.create_linear_file_index_bin_array(bin_value=lambda_value * 1e-10)   # to switch to seconds
            o_bin.create_linear_bin_arrays()

        else:
            raise NotImplementedError("bin auto linear algorithm not implemented!")

        self.logger.info(f"-> file_index_array_binned: {o_bin.linear_bins[TimeSpectraKeys.file_index_array]}")
        self.logger.info(f"-> tof_array_binned: {o_bin.linear_bins[TimeSpectraKeys.tof_array]}")
        self.logger.info(f"-> lambda_array_binned: {o_bin.linear_bins[TimeSpectraKeys.lambda_array]}")

        self.parent.linear_bins = {TimeSpectraKeys.file_index_array: o_bin.get_linear_file_index(),
                                   TimeSpectraKeys.tof_array: o_bin.get_linear_tof(),
                                   TimeSpectraKeys.lambda_array: o_bin.get_linear_lambda()}

        self.fill_auto_table()
        self.refresh_tab()

        show_status_message(parent=self.parent,
                            message=f"New {source_radio_button} bin size selected!",
                            status=StatusMessageStatus.ready,
                            duration_s=5)

        self.parent.ui.auto_linear_file_index_spinBox.blockSignals(False)
        self.parent.ui.auto_linear_tof_doubleSpinBox.blockSignals(False)
        self.parent.ui.auto_linear_lambda_doubleSpinBox.blockSignals(False)

    def fill_auto_table(self):
        o_table = TableHandler(table_ui=self.parent.ui.bin_auto_tableWidget)
        o_table.remove_all_rows()

        o_get = Get(parent=self.parent)
        bin_auto_mode = o_get.bin_auto_mode()

        if bin_auto_mode == BinAutoMode.linear:
            bins = self.parent.linear_bins
        else:
            bins = self.parent.log_bins

        list_rows = np.arange(len(bins[TimeSpectraKeys.file_index_array]))

        file_index_array_of_bins = bins[TimeSpectraKeys.file_index_array]
        tof_array_of_bins = bins[TimeSpectraKeys.tof_array]
        lambda_array_of_bins = bins[TimeSpectraKeys.lambda_array]

        for _row in np.arange(len(list_rows)):

            file_bin = file_index_array_of_bins[_row]
            tof_bin = tof_array_of_bins[_row]
            lambda_bin = lambda_array_of_bins[_row]

            if file_bin == []:
                str_file_index = "N/A"
                str_tof = "N/A"
                str_lambda = "N/A"

            elif len(file_bin) == 1:
                str_file_index = file_bin[0]
                str_tof = f"{tof_bin[0] * TO_MICROS_UNITS: .2f}"
                str_lambda = f"{lambda_bin[0] * TO_ANGSTROMS_UNITS: .3f}"

            elif len(file_bin) == 2:
                str_file_index = f"{file_bin[0]}, {file_bin[1]}"
                str_tof = f"{tof_bin[0] * TO_MICROS_UNITS:.2f}, " \
                          f"{tof_bin[1] * TO_MICROS_UNITS:.2f}"
                str_lambda = f"{lambda_bin[0] * TO_ANGSTROMS_UNITS:.3f}, " \
                             f"{lambda_bin[1] * TO_ANGSTROMS_UNITS:.3f}"

            else:
                str_file_index = f"{file_bin[0]} ... {file_bin[-1]}"
                str_tof = f"{tof_bin[0] * TO_MICROS_UNITS:.2f} ... " \
                          f"{tof_bin[-1] * TO_MICROS_UNITS:.2f}"
                str_lambda = f"{lambda_bin[0] * TO_ANGSTROMS_UNITS:.3f} ... " \
                             f"{lambda_bin[-1] * TO_ANGSTROMS_UNITS:.3f}"

            o_table.insert_empty_row(row=_row)
            o_table.insert_item(row=_row, column=0, value=_row, editable=False)
            o_table.insert_item(row=_row, column=1, value=str_file_index, editable=False)
            o_table.insert_item(row=_row, column=2, value=str_tof, editable=False)
            o_table.insert_item(row=_row, column=3, value=str_lambda, editable=False)

    def auto_linear_radioButton_changed(self):
        file_index_status = False
        tof_status = False
        lambda_status = False
        if self.parent.ui.auto_linear_file_index_radioButton.isChecked():
            file_index_status = True
            source_button = TimeSpectraKeys.file_index_array
        elif self.parent.ui.auto_linear_tof_radioButton.isChecked():
            tof_status = True
            source_button = TimeSpectraKeys.tof_array
        else:
            lambda_status = True
            source_button = TimeSpectraKeys.lambda_array

        self.parent.ui.auto_linear_file_index_spinBox.setEnabled(file_index_status)
        self.parent.ui.auto_linear_tof_doubleSpinBox.setEnabled(tof_status)
        self.parent.ui.bin_auto_linear_tof_units_label.setEnabled(tof_status)
        self.parent.ui.auto_linear_lambda_doubleSpinBox.setEnabled(lambda_status)
        self.parent.ui.bin_auto_linear_lambda_units_label.setEnabled(lambda_status)

        self.bin_auto_linear_changed(source_radio_button=source_button)

    def auto_log_radioButton_changed(self):
        file_index_status = False
        tof_status = False
        lambda_status = False
        if self.parent.ui.bin_auto_log_file_index_radioButton.isChecked():
            file_index_status = True
            source_button = TimeSpectraKeys.file_index_array
        elif self.parent.ui.bin_auto_log_tof_radioButton.isChecked():
            tof_status = True
            source_button = TimeSpectraKeys.tof_array
        else:
            lambda_status = True
            source_button = TimeSpectraKeys.lambda_array

        self.parent.ui.auto_log_file_index_spinBox.setEnabled(file_index_status)
        self.parent.ui.auto_log_tof_doubleSpinBox.setEnabled(tof_status)
        self.parent.ui.auto_log_lambda_doubleSpinBox.setEnabled(lambda_status)

        self.bin_auto_log_changed(source_radio_button=source_button)
