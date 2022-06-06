import copy
import logging
import numpy as np

from ..session import SessionKeys
from ..utilities import BinMode
from ..utilities.get import Get
from ..utilities import TimeSpectraKeys
from .. import LAMBDA, MICRO, ANGSTROMS
from .bin import Bin
from ..utilities.table_handler import TableHandler


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent
        self.logger = logging.getLogger('maverick')

    def refresh_tab(self):
        # refresh profile using right x_axis
        self.parent.bin_profile_view.clear()
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
            raise NotImplementedError("Bin mode not implemented!")

    def bin_auto_log_changed(self, source_radio_button=TimeSpectraKeys.file_index_array):
        if source_radio_button == TimeSpectraKeys.file_index_array:
            file_index_value = self.parent.ui.auto_log_file_index_spinBox.value()

        elif source_radio_button == TimeSpectraKeys.tof_array:
            tof_value = self.parent.ui.auto_log_tof_doubleSpinBox.value()

        elif source_radio_button == TimeSpectraKeys.lambda_array:
            lambda_value = self.parent.ui.auto_log_lambda_doubleSpinBox.value()

        else:
            raise NotImplementedError("bin auto log algorithm not implemented!")

    def bin_auto_linear_changed(self, source_radio_button=TimeSpectraKeys.file_index_array):
        self.logger.info(f"bin auto linear changed: {source_radio_button}")
        o_bin = Bin(parent=self.parent)
        self.parent.ui.auto_linear_file_index_spinBox.blockSignals(True)
        self.parent.ui.auto_linear_tof_doubleSpinBox.blockSignals(True)
        self.parent.ui.auto_linear_lambda_doubleSpinBox.blockSignals(True)

        self.logger.info(f"-> raw_file_index_array_binned: {self.parent.time_spectra[TimeSpectraKeys.file_index_array]}")
        self.logger.info(f"-> raw_tof_array_binned: {self.parent.time_spectra[TimeSpectraKeys.tof_array]}")
        self.logger.info(f"-> raw_lambda_array_binned: {self.parent.time_spectra[TimeSpectraKeys.lambda_array]}")

        if source_radio_button == TimeSpectraKeys.file_index_array:
            file_index_value = self.parent.ui.auto_linear_file_index_spinBox.value()
            o_bin.create_linear_file_index_bin_array(file_index_value)
            o_bin.create_linear_bin_arrays(source_array=source_radio_button)

            delta_tof = o_bin.get_linear_delta_tof() * 1e6  # to display in micros
            self.parent.ui.auto_linear_tof_doubleSpinBox.setValue(delta_tof)
            #
            # delta_lambda = o_bin.get_linear_delta_lambda() * 1e10  # to display in Angstroms
            # self.parent.ui.auto_linear_lambda_doubleSpinBox.setValue(delta_lambda)

        # elif source_radio_button == TimeSpectraKeys.tof_array:
        #     tof_value = self.parent.ui.auto_linear_tof_doubleSpinBox.value()
        #     o_bin.create_linear_tof_bin_array(tof_value * 1e-6)   # to switch to seconds
        #     o_bin.create_linear_bin_arrays(source_array=source_radio_button)
        #
        #     delta_file_index = o_bin.get_linear_delta_file_index()
        #     self.parent.ui.auto_linear_file_index_spinBox.setValue(delta_file_index)
        #
        #     delta_lambda = o_bin.get_linear_delta_lambda() * 1e10  # to display in Angstroms
        #     self.parent.ui.auto_linear_lambda_doubleSpinBox.setValue(delta_lambda)
        #
        # elif source_radio_button == TimeSpectraKeys.lambda_array:
        #     lambda_value = self.parent.ui.auto_linear_lambda_doubleSpinBox.value()
        #     o_bin.create_linear_lambda_array(lambda_value * 1e-10)  # to move to m
        #     o_bin.create_linear_bin_arrays(source_array=source_radio_button)
        #
        #     delta_file_index = o_bin.get_linear_delta_file_index()
        #     self.parent.ui.auto_linear_file_index_spinBox.setValue(delta_file_index)
        #
        #     delta_tof = o_bin.get_linear_delta_tof() * 1e6  # to display in micros
        #     self.parent.ui.auto_linear_tof_doubleSpinBox.setValue(delta_tof)

        else:
            raise NotImplementedError("bin auto linear algorithm not implemented!")

        self.logger.info(f"-> file_index_array_binned: {o_bin.linear_bins[TimeSpectraKeys.file_index_array]}")
        self.logger.info(f"-> tof_array_binned: {o_bin.linear_bins[TimeSpectraKeys.tof_array]}")
        # self.logger.info(f"-> lambda_array_binned: {o_bin.linear_bins[TimeSpectraKeys.lambda_array]}")

        self.parent.ui.auto_linear_file_index_spinBox.blockSignals(False)
        self.parent.ui.auto_linear_tof_doubleSpinBox.blockSignals(False)
        self.parent.ui.auto_linear_lambda_doubleSpinBox.blockSignals(False)

        self.parent.linear_bins = {TimeSpectraKeys.file_index_array: o_bin.get_linear_file_index(),
                                   TimeSpectraKeys.tof_array: o_bin.get_linear_tof(),
                                   TimeSpectraKeys.lambda_array: o_bin.get_linear_lambda()}

        # self.fill_auto_table()

    def fill_auto_table(self):
        o_table = TableHandler(table_ui=self.parent.ui.bin_auto_tableWidget)
        o_table.remove_all_rows()

        linear_bins = self.parent.linear_bins
        list_rows = np.arange(len(linear_bins[TimeSpectraKeys.file_index_array]))

        file_index_array = linear_bins[TimeSpectraKeys.file_index_array]
        tof_array = linear_bins[TimeSpectraKeys.tof_array]
        lambda_array = linear_bins[TimeSpectraKeys.lambda_array]

        _row = 0
        for _row in np.arange(len(list_rows)-1):
            left_file_index = file_index_array[_row]
            right_file_index = file_index_array[_row+1]
            str_file_index = f"[{left_file_index}, {right_file_index})"

            left_tof = tof_array[_row] * 1e6  # to display in micros
            right_tof = tof_array[_row+1] * 1e6
            str_tof = f"[{left_tof:.2f}, {right_tof:.2f})"

            left_lambda = lambda_array[_row] * 1e10  # to display in Angstroms
            right_lambda = lambda_array[_row+1] * 1e10
            str_lambda = f"[{left_lambda:.3f}, {right_lambda:.3f})"

            o_table.insert_empty_row(row=_row)
            o_table.insert_item(row=_row, column=0, value=_row, editable=False)
            o_table.insert_item(row=_row, column=1, value=str_file_index, editable=False)
            o_table.insert_item(row=_row, column=2, value=str_tof, editable=False)
            o_table.insert_item(row=_row, column=3, value=str_lambda, editable=False)
