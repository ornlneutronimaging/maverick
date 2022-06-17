import os
from os.path import expanduser
from pathlib import Path
import configparser
import copy
import numpy as np

from . import CombineAlgorithm, TimeSpectraKeys, BinAutoMode, BinMode, BinAlgorithm
from ..session import SessionKeys
from ..bin import StatisticsName


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

    def bin_mode(self):
        if self.parent.ui.bin_tabWidget.currentIndex() == 0:
            return BinMode.auto
        elif self.parent.ui.bin_tabWidget.currentIndex() == 1:
            return BinMode.manual
        else:
            raise NotImplementedError("tab not implemented!")

    def bin_auto_mode(self):
        if self.parent.ui.auto_log_radioButton.isChecked():
            return BinAutoMode.log
        elif self.parent.ui.auto_linear_radioButton.isChecked():
            return BinAutoMode.linear
        else:
            raise NotImplementedError("auto bin mode not implemented!")

    def bin_x_axis_selected(self):
        if self.parent.ui.bin_file_index_radioButton.isChecked():
            return TimeSpectraKeys.file_index_array
        elif self.parent.ui.bin_tof_radioButton.isChecked():
            return TimeSpectraKeys.tof_array
        elif self.parent.ui.bin_lambda_radioButton.isChecked():
            return TimeSpectraKeys.lambda_array
        else:
            raise NotImplementedError("xaxis not implemented in bin tab!")

    def auto_log_bin_requested(self):
        if self.parent.ui.bin_auto_log_file_index_radioButton.isChecked():
            return self.parent.ui.auto_log_file_index_spinBox.value()
        elif self.parent.ui.bin_auto_log_tof_radioButton.isChecked():
            return self.parent.ui.auto_log_tof_doubleSpinBox.value()
        elif self.parent.ui.bin_auto_log_lambda_radioButton.isChecked():
            return self.parent.ui.auto_log_lambda_doubleSpinBox.value()
        else:
            raise NotImplementedError(f"auto log bin algorithm not implemented!")

    def auto_bins_currently_activated(self):
        auto_bin_mode = self.bin_auto_mode()
        if auto_bin_mode == BinAutoMode.linear:
            return self.parent.linear_bins
        elif auto_bin_mode == BinAutoMode.log:
            return self.parent.log_bins
        else:
            raise NotImplementedError("Auto bin mode not implemented!")

    def bin_log_axis(self):
        if self.parent.ui.bin_auto_log_file_index_radioButton.isChecked():
            return TimeSpectraKeys.file_index_array
        elif self.parent.ui.bin_auto_log_tof_radioButton.isChecked():
            return TimeSpectraKeys.tof_array
        elif self.parent.ui.bin_auto_log_lambda_radioButton.isChecked():
            return TimeSpectraKeys.lambda_array
        else:
            raise NotImplementedError(f"type not supported")

    def bin_linear_axis(self):
        if self.parent.ui.auto_linear_file_index_radioButton.isChecked():
            return TimeSpectraKeys.file_index_array
        elif self.parent.ui.auto_linear_tof_radioButton.isChecked():
            return TimeSpectraKeys.tof_array
        elif self.parent.ui.auto_linear_lambda_radioButton.isChecked():
            return TimeSpectraKeys.lambda_array
        else:
            raise NotImplementedError(f"type not supported")

    def bin_add_method(self):
        if self.parent.ui.bin_mean_radioButton.isChecked():
            return BinAlgorithm.mean
        elif self.parent.ui.bin_median_radioButton.isChecked():
            return BinAlgorithm.median
        else:
            raise NotImplementedError("Bin method to add images not supported")

    def current_bin_tab_working_axis(self):
        bin_mode = self.bin_auto_mode()
        if bin_mode == BinAutoMode.log:
            return self.bin_log_axis()
        elif bin_mode == BinAutoMode.linear:
            return self.bin_linear_axis()
        else:
            raise NotImplementedError(f"type not supported")

    def bin_statistics_plot_requested(self):
        current_index = self.parent.ui.bin_stats_comboBox.currentIndex()
        list_name = [StatisticsName.mean,
                     StatisticsName.median,
                     StatisticsName.std,
                     StatisticsName.min,
                     StatisticsName.max]
        return list_name[current_index]

    def list_array_to_combine(self):
        session = self.parent.session
        list_working_folders_status = session[SessionKeys.list_working_folders_status]
        raw_data_folders = self.parent.raw_data_folders
        list_working_folders = session[SessionKeys.list_working_folders]

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

    def manual_working_row(self, working_item_id=None):
        list_item_id = self.parent.list_of_manual_bins_item
        for _row, item in enumerate(list_item_id):
            if item == working_item_id:
                return _row
        return -1

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
