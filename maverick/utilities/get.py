import os
from os.path import expanduser
from pathlib import Path
import configparser


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

    @staticmethod
    def full_home_file_name(base_file_name):
        home_folder = expanduser("~")
        full_log_file_name = os.path.join(home_folder, base_file_name)
        return full_log_file_name
