import glob
import os
from pathlib import Path

from ..utilities import math_tools as math_tools

from neutronbraggedge.experiment_handler.tof import TOF
from neutronbraggedge.experiment_handler.experiment import Experiment

TIME_SPECTRA_NAME_FORMAT = '*_Spectra.txt'


class GetTimeSpectraFilename:
    __slots__ = ['parent', 'file_found', 'time_spectra', 'time_spectra_name_format', 'folder']

    def __init__(self, parent=None, folder=None):
        self.parent = parent
        self.file_found = False
        self.time_spectra = ''
        self.time_spectra_name_format = '*_Spectra.txt'
        self.folder = folder

    def retrieve_file_name(self):
        time_spectra = glob.glob(self.folder + '/' + TIME_SPECTRA_NAME_FORMAT)
        if time_spectra and os.path.exists(time_spectra[0]):
            return f"{time_spectra[0]}"

        else:
            return ""


class TimeSpectraHandler:
    tof_array = []
    lambda_array = []
    counts_array = []
    full_file_name = ''

    def __init__(self, parent=None, time_spectra_file_name=None):
        self.tof_array = []
        self.parent = parent

        filename = time_spectra_file_name

        self.short_file_name = Path(filename).name
        self.full_file_name = Path(filename)

    def load(self):
        if self.full_file_name.is_file():

            _tof_handler = TOF(filename=str(self.full_file_name))
            _tof_array_s = _tof_handler.tof_array
            # self.tof_array = _tof_array_s * 1e6
            self.tof_array = _tof_array_s
            self.counts_array = _tof_handler.counts_array

    def calculate_lambda_scale(self):
        distance_source_detector = self.parent.ui.distance_source_detector_doubleSpinBox.value()
        detector_offset = self.parent.ui.detector_offset_spinBox.value()

        _exp = Experiment(tof=self.tof_array,
                          distance_source_detector_m=distance_source_detector,
                          detector_offset_micros=detector_offset)
        self.lambda_array = _exp.lambda_array
        