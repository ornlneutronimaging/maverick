import copy

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
