import os
from os.path import expanduser
from pathlib import Path
import configparser

from . import CombineAlgorithm
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

    def version(self):
        setup_cfg = 'setup.cfg'
        this_folder = os.path.abspath(os.path.dirname(__file__))
        top_path = Path(this_folder).parent.parent
        full_path_setup_cfg = str(Path(top_path) / Path(setup_cfg))
        config = configparser.ConfigParser()
        config.read(full_path_setup_cfg)
        version = config['metadata']['version']
        return version

    def combine_algorithm(self):
        if self.parent.ui.combine_mean_radioButton.isChecked():
            return CombineAlgorithm.mean
        elif self.parent.ui.combine_median_radioButton.isChecked():
            return CombineAlgorithm.median
        else:
            raise NotImplementedError("Combine algorithm not implemented!")

    def list_array_to_combine(self):
        session = self.parent.session
        list_working_folders_status = session[SessionKeys.list_working_folders_status]
        raw_data_folders = self.parent.raw_data_folders
        list_working_folders = session[SessionKeys.list_working_folders]

        list_array = []
        for _status, _folder_name in zip(list_working_folders_status, list_working_folders):
            if _status:
                list_array.append(raw_data_folders[_folder_name]['data'])
        return list_array

    @staticmethod
    def full_home_file_name(base_file_name):
        home_folder = expanduser("~")
        full_log_file_name = os.path.join(home_folder, base_file_name)
        return full_log_file_name
