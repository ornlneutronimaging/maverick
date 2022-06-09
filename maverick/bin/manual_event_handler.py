import logging

from ..utilities import TimeSpectraKeys, BinAutoMode, BinMode
from .plot import Plot


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
