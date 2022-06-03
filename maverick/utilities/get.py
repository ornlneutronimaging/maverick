import os
from os.path import expanduser
from pathlib import Path
import configparser
import copy
import numpy as np

from . import CombineAlgorithm, TimeSpectraKeys
from ..session import SessionKeys


class Get:

    def __init__(self, parent=None):
        self.parent = parent

    def log_file_name(self):
        log_file_name = self.parent.config['log_file_name']
        full_log_file_name = Get.full_home_file_name(log_file_name)
        return full_log_file_name

    def automatic_config_file_name(self):
        config_file_name = self.parent.config['session_file_name']
        full_config_file_name = Get.full_home_file_name(config_file_name)
        return full_config_file_name

    def combine_algorithm(self):
        if self.parent.ui.combine_mean_radioButton.isChecked():
            return CombineAlgorithm.mean
        elif self.parent.ui.combine_median_radioButton.isChecked():
            return CombineAlgorithm.median
        else:
            raise NotImplementedError("Combine algorithm not implemented!")

    def combine_x_axis_selected(self):
        if self.parent.combine_file_index_radio_button.isChecked():
            return TimeSpectraKeys.file_index_array
        elif self.parent.tof_radio_button.isChecked():
            return TimeSpectraKeys.tof_array
        elif self.parent.lambda_radio_button.isChecked():
            return TimeSpectraKeys.lambda_array
        else:
            raise NotImplementedError("xaxis not implemented in the combine tab!")

    def bin_x_axis_selected(self):
        if self.parent.ui.bin_file_index_radioButton.isChecked():
            return TimeSpectraKeys.file_index_array
        elif self.parent.ui.bin_tof_radioButton.isChecked():
            return TimeSpectraKeys.tof_array
        elif self.parent.ui.bin_lambda_radioButton.isChecked():
            return TimeSpectraKeys.lambda_array
        else:
            raise NotImplementedError("xaxis not implemented in bin tab!")

    def list_array_to_combine(self):
        session = self.parent.session
        list_working_folders_status = session[SessionKeys.list_working_folders_status]
        raw_data_folders = self.parent.raw_data_folders
        list_working_folders = session[SessionKeys.list_working_folders]

        import numpy as np

        list_array = []
        for _status, _folder_name in zip(list_working_folders_status, list_working_folders):
            if _status:
                list_array.append(copy.deepcopy(raw_data_folders[_folder_name]['data']))

        return list_array

    def list_of_folders_to_use(self):
        session = self.parent.session
        list_working_folders_status = session[SessionKeys.list_working_folders_status]
        list_working_folders = np.array(session[SessionKeys.list_working_folders])
        return list_working_folders[list_working_folders_status]

    @staticmethod
    def full_home_file_name(base_file_name):
        home_folder = expanduser("~")
        full_log_file_name = os.path.join(home_folder, base_file_name)
        return full_log_file_name

    @staticmethod
    def version():
        setup_cfg = 'setup.cfg'
        this_folder = os.path.abspath(os.path.dirname(__file__))
        top_path = Path(this_folder).parent.parent
        full_path_setup_cfg = str(Path(top_path) / Path(setup_cfg))
        config = configparser.ConfigParser()
        config.read(full_path_setup_cfg)
        version = config['metadata']['version']
        return version
