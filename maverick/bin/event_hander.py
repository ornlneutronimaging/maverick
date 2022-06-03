import copy
import logging

from ..session import SessionKeys
from ..utilities import BinMode
from ..utilities.get import Get
from ..utilities import TimeSpectraKeys
from .. import LAMBDA, MICRO, ANGSTROMS
from .bin import Bin


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
        if source_radio_button == TimeSpectraKeys.file_index_array:
            file_index_value = self.parent.ui.auto_linear_file_index_spinBox.value()
            o_bin.create_linear_file_index_bin_array(file_index_value)
            o_bin.create_linear_axis(source_array=source_radio_button)

            delta_tof = o_bin.get_linear_delta_tof() * 1e6  # to display in micros
            self.parent.ui.auto_linear_tof_doubleSpinBox.setValue(delta_tof)

            delta_lambda = o_bin.get_linear_delta_lambda() * 1e10  # to display in Angstroms
            self.parent.ui.auto_linear_lambda_doubleSpinBox.setValue(delta_lambda)

        elif source_radio_button == TimeSpectraKeys.tof_array:
            tof_value = self.parent.ui.auto_linear_tof_doubleSpinBox.value()
            o_bin.create_linear_tof_bin_array(tof_value / 1e6)   # to switch to seconds
            o_bin.create_linear_axis(source_array=source_radio_button)

            delta_file_index = o_bin.get_linear_delta_file_index()
            self.parent.ui.auto_linear_file_index_spinBox.setValue(delta_file_index)

            delta_lambda = o_bin.get_linear_delta_lambda() * 1e10  # to display in Angstroms
            self.parent.ui.auto_linear_lambda_doubleSpinBox.setValue(delta_lambda)

        elif source_radio_button == TimeSpectraKeys.lambda_array:
            lambda_value = self.parent.ui.auto_linear_lambda_doubleSpinBox.value()

        else:
            raise NotImplementedError("bin auto linear algorithm not implemented!")

        self.logger.info(f"-> file_index_array_binned: {o_bin.linear_bins[TimeSpectraKeys.file_index_array]}")
        self.logger.info(f"-> tof_array_binned: {o_bin.linear_bins[TimeSpectraKeys.tof_array]}")
        self.logger.info(f"-> lambda_array_binned: {o_bin.linear_bins[TimeSpectraKeys.lambda_array]}")

        self.parent.ui.auto_linear_file_index_spinBox.blockSignals(False)
        self.parent.ui.auto_linear_tof_doubleSpinBox.blockSignals(False)
        self.parent.ui.auto_linear_lambda_doubleSpinBox.blockSignals(False)
