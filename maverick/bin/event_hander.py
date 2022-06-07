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

BIN_MARGIN_COEFF = 0.1


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent
        self.logger = logging.getLogger('maverick')

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
            x_axis *= 1e6    # to display axis in micros
            x_axis_label = "tof (" + MICRO + "s)"
        elif time_spectra_x_axis_name == TimeSpectraKeys.lambda_array:
            x_axis *= 1e10    # to display axis in Angstroms
            x_axis_label = LAMBDA + "(" + ANGSTROMS + ")"

        self.parent.bin_profile_view.plot(x_axis, profile_signal, pen='r', symbol='x')
        self.parent.bin_profile_view.setLabel("left", f"{combine_algorithm} counts")
        self.parent.bin_profile_view.setLabel("bottom", x_axis_label)

        if o_get.bin_auto_mode() == BinAutoMode.linear:
            bins = self.parent.linear_bins[time_spectra_x_axis_name]
            list_item = []
            for _bin in bins:

                if time_spectra_x_axis_name == TimeSpectraKeys.file_index_array:
                    scale_bin = [_bin[0], _bin[1] - BIN_MARGIN_COEFF]
                elif time_spectra_x_axis_name == TimeSpectraKeys.tof_array:
                    coeff = 1e6
                    scale_bin = [_value * coeff for _value in _bin]
                    right_margin = BIN_MARGIN_COEFF * (x_axis[1] - x_axis[0])
                    scale_bin[1] -= right_margin
                elif time_spectra_x_axis_name == TimeSpectraKeys.lambda_array:
                    coeff = 1e10
                    scale_bin = [_value * coeff for _value in _bin]
                    right_margin = BIN_MARGIN_COEFF * (x_axis[1] - x_axis[0])
                    scale_bin[1] -= right_margin

                item = pg.LinearRegionItem(values=scale_bin,
                                           orientation='vertical',
                                           brush=None,
                                           movable=False,
                                           bounds=None)
                item.setZValue(-10)
                self.parent.bin_profile_view.addItem(item)
                list_item.append(item)

            self.parent.list_bins_items = list_item

        else:
            pass

    def bin_auto_radioButton_clicked(self):
        state_auto = self.parent.ui.auto_log_radioButton.isChecked()
        self.parent.ui.bin_auto_log_frame.setEnabled(state_auto)
        self.parent.ui.bin_auto_linear_frame.setEnabled(not state_auto)

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

        if source_radio_button == TimeSpectraKeys.file_index_array:
            file_index_value = self.parent.ui.auto_log_file_index_spinBox.value()
            self.logger.info(f"--> bin requested: {file_index_value}")

        elif source_radio_button == TimeSpectraKeys.tof_array:
            tof_value = self.parent.ui.auto_log_tof_doubleSpinBox.value()
            self.logger.info(f"--> bin requested: {tof_value}")
            o_bin.create_log_file_index_bin_array(bin_value=tof_value)
            # o_bin.create_log_bin_arrays()

        elif source_radio_button == TimeSpectraKeys.lambda_array:
            lambda_value = self.parent.ui.auto_log_lambda_doubleSpinBox.value()
            self.logger.info(f"--> bin requested: {lambda_value}")
            o_bin.create_log_file_index_bin_array(bin_value=lambda_value)
            # o_bin.create_log_bin_arrays()

        else:
            raise NotImplementedError("bin auto log algorithm not implemented!")

        self.logger.info(f"-> file_index_array_binned: {o_bin.log_bins[TimeSpectraKeys.file_index_array]}")
        self.logger.info(f"-> tof_array_binned: {o_bin.log_bins[TimeSpectraKeys.tof_array]}")
        self.logger.info(f"-> lambda_array_binned: {o_bin.log_bins[TimeSpectraKeys.lambda_array]}")

        self.parent.ui.auto_log_file_index_spinBox.blockSignals(False)
        self.parent.ui.auto_log_tof_doubleSpinBox.blockSignals(False)
        self.parent.ui.auto_log_lambda_doubleSpinBox.blockSignals(False)

        del o_bin

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

        # try:

        if source_radio_button == TimeSpectraKeys.file_index_array:
            file_index_value = self.parent.ui.auto_linear_file_index_spinBox.value()
            self.logger.info(f"--> bin requested: {file_index_value}")
            o_bin.create_linear_file_index_bin_array(bin_value=file_index_value)
            # o_bin.create_linear_bin_arrays()
            #
            # delta_tof = o_bin.get_linear_delta_tof() * 1e6  # to display in micros
            # self.parent.ui.auto_linear_tof_doubleSpinBox.setValue(delta_tof)
            #
            # delta_lambda = o_bin.get_linear_delta_lambda() * 1e10  # to display in Angstroms
            # self.parent.ui.auto_linear_lambda_doubleSpinBox.setValue(delta_lambda)

        elif source_radio_button == TimeSpectraKeys.tof_array:
            tof_value = self.parent.ui.auto_linear_tof_doubleSpinBox.value()
            self.logger.info(f"--> bin requested: {tof_value}")
            o_bin.create_linear_file_index_bin_array(bin_value=tof_value * 1e-6)   # to switch to seconds
            # o_bin.create_linear_bin_arrays()
            #
            # delta_file_index = o_bin.get_linear_delta_file_index()
            # self.parent.ui.auto_linear_file_index_spinBox.setValue(delta_file_index)
            #
            # delta_lambda = o_bin.get_linear_delta_lambda() * 1e10  # to display in Angstroms
            # self.parent.ui.auto_linear_lambda_doubleSpinBox.setValue(delta_lambda)

        elif source_radio_button == TimeSpectraKeys.lambda_array:
            lambda_value = self.parent.ui.auto_linear_lambda_doubleSpinBox.value()
            self.logger.info(f"--> bin requested: {lambda_value}")
            o_bin.create_linear_file_index_bin_array(bin_value=lambda_value * 1e-10)   # to switch to seconds
            # o_bin.create_linear_bin_arrays()
            #
            # delta_file_index = o_bin.get_linear_delta_file_index()
            # self.parent.ui.auto_linear_file_index_spinBox.setValue(delta_file_index)
            #
            # delta_tof = o_bin.get_linear_delta_tof() * 1e6  # to display in micros
            # self.parent.ui.auto_linear_tof_doubleSpinBox.setValue(delta_tof)

        else:
            raise NotImplementedError("bin auto linear algorithm not implemented!")

        # self.logger.info(f"-> file_index_array_binned: {o_bin.linear_bins[TimeSpectraKeys.file_index_array]}")
        # self.logger.info(f"-> tof_array_binned: {o_bin.linear_bins[TimeSpectraKeys.tof_array]}")
        # self.logger.info(f"-> lambda_array_binned: {o_bin.linear_bins[TimeSpectraKeys.lambda_array]}")
        #
        # self.parent.linear_bins = {TimeSpectraKeys.file_index_array: o_bin.get_linear_file_index(),
        #                            TimeSpectraKeys.tof_array: o_bin.get_linear_tof(),
        #                            TimeSpectraKeys.lambda_array: o_bin.get_linear_lambda()}
        #
        # self.fill_auto_table()
        # self.refresh_tab()
        #
        # show_status_message(parent=self.parent,
        #                     message=f"New {source_radio_button} bin size selected!",
        #                     status=StatusMessageStatus.ready,
        #                     duration_s=5)

        # except IndexError:
        #     show_status_message(parent=self.parent,
        #                         message="Error - Try selecting a smaller bin size!",
        #                         status=StatusMessageStatus.error,
        #                         duration_s=5)

        self.parent.ui.auto_linear_file_index_spinBox.blockSignals(False)
        self.parent.ui.auto_linear_tof_doubleSpinBox.blockSignals(False)
        self.parent.ui.auto_linear_lambda_doubleSpinBox.blockSignals(False)

    def fill_auto_table(self):
        o_table = TableHandler(table_ui=self.parent.ui.bin_auto_tableWidget)
        o_table.remove_all_rows()

        linear_bins = self.parent.linear_bins
        list_rows = np.arange(len(linear_bins[TimeSpectraKeys.file_index_array]))

        file_index_array_of_bins = linear_bins[TimeSpectraKeys.file_index_array]
        tof_array_of_bins = linear_bins[TimeSpectraKeys.tof_array]
        lambda_array_of_bins = linear_bins[TimeSpectraKeys.lambda_array]

        for _row in np.arange(len(list_rows)):
            if file_index_array_of_bins[_row] == []:
                str_file_index = "N/A"
            else:
                from_file_index = file_index_array_of_bins[_row][0]
                to_file_index = file_index_array_of_bins[_row][1]
                str_file_index = f"[{from_file_index}, {to_file_index})"

            if str_file_index == "N/A":
                str_tof = "N/A"
            else:
                left_tof = tof_array_of_bins[_row][0] * 1e6  # to display in micros
                right_tof = tof_array_of_bins[_row][1] * 1e6
                str_tof = f"[{left_tof:.2f}, {right_tof:.2f})"

            if str_file_index == "N/A":
                str_lambda = "N/A"
            else:
                left_lambda = lambda_array_of_bins[_row][0] * 1e10  # to display in Angstroms
                right_lambda = lambda_array_of_bins[_row][1] * 1e10
                str_lambda = f"[{left_lambda:.3f}, {right_lambda:.3f})"

            o_table.insert_empty_row(row=_row)
            o_table.insert_item(row=_row, column=0, value=_row, editable=False)
            o_table.insert_item(row=_row, column=1, value=str_file_index, editable=False)
            o_table.insert_item(row=_row, column=2, value=str_tof, editable=False)
            o_table.insert_item(row=_row, column=3, value=str_lambda, editable=False)
