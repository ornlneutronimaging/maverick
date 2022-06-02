import copy

from ..session import SessionKeys
from ..utilities import BinMode
from ..utilities.get import Get
from ..utilities import TimeSpectraKeys
from .. import LAMBDA, MICRO, ANGSTROMS


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

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


        # display bins line according to bin defined on the left side
        self.update_bin_autoradiobutton_delta_t_units()

    def update_bin_autoradiobutton_delta_t_units(self):
        o_get = Get(parent=self.parent)
        time_spectra_x_axis_name = o_get.bin_x_axis_selected()
        if time_spectra_x_axis_name == TimeSpectraKeys.file_index_array:
            x_axis_label = "file index"
        elif time_spectra_x_axis_name == TimeSpectraKeys.tof_array:
            x_axis_label = MICRO + "s"
        elif time_spectra_x_axis_name == TimeSpectraKeys.lambda_array:
            x_axis_label = ANGSTROMS
        self.parent.ui.auto_delta_t_units_label.setText(x_axis_label)

    def bin_auto_radioButton_clicked(self):
        state_auto = self.parent.ui.bin_auto_delta_t_over_t_radioButton.isChecked()
        self.parent.ui.bin_auto_delta_t_over_t_doubleSpinBox.setEnabled(state_auto)
        self.parent.ui.bin_auto_delta_t_doubleSpinBox.setEnabled(not state_auto)
        self.parent.ui.auto_delta_t_units_label.setEnabled(not state_auto)

    def bin_auto_manual_tab_changed(self, new_tab_index=0):
        if new_tab_index == 0:
            self.parent.session[SessionKeys.bin_mode] = BinMode.auto
        elif new_tab_index == 1:
            self.parent.session[SessionKeys.bin_mode] = BinMode.manual
        else:
            raise NotImplementedError("Bin mode not implemented!")
