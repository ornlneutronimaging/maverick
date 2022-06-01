import os
from qtpy.QtWidgets import QFileDialog, QCheckBox
import logging
import numpy as np

from ..utilities.file_handler import FileHandler
from ..utilities.table_handler import TableHandler
from ..utilities.time_spectra import GetTimeSpectraFilename, TimeSpectraHandler
from ..utilities import TimeSpectraKeys
from ..session import SessionKeys
from ..load.load_files import LoadFiles


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent
        self.logger = logging.getLogger('maverick')

    def select_top_folder(self):
        _folder = str(str(QFileDialog.getExistingDirectory(caption="Select Top Working Folder",
                                                           directory=self.parent.session[SessionKeys.top_folder],
                                                           options=QFileDialog.ShowDirsOnly)))
        if _folder == "":
            self.logger.info("User Canceled the selection of top folder dialog!")
            return

        self.logger.info(f"Users selected a new top folder: {_folder}")

        # get list of folders in top folder
        self.parent.session[SessionKeys.top_folder] = os.path.abspath(_folder)
        list_folders = FileHandler.get_list_of_folders(_folder)
        self.parent.session[SessionKeys.list_working_folders] = list_folders

        # initialize parameters when using new working folder
        self.reset_data()

        # display the full path of the top folder selected
        self.parent.ui.top_folder_label.setText(_folder)

        # display list of folders in widget and column showing working folders used
        self.populate_list_of_folders_to_combine()

    def reset_data(self):
        """
        This re-initialize all the parameters when working with a new top folder
        """

        # reset master dictionary that contains the raw data
        list_folders = self.parent.session[SessionKeys.list_working_folders]
        _data_dict = {}
        for _folder in list_folders:
            list_files = FileHandler.get_list_of_files(_folder)
            nbr_files = len(list_files)
            _data_dict[_folder] = {'data': None,
                                   'list_files': list_files,
                                   'nbr_files': nbr_files,
                                   }
        self.parent.raw_data_folders = _data_dict

        # initialize list of selected folders
        self.parent.session[SessionKeys.list_working_folders_status] = [False for _index in np.arange(len(list_folders))]

        # reset time spectra
        self.parent.time_spectra = {TimeSpectraKeys.file_name: None,
                                    TimeSpectraKeys.tof_array: None,
                                    TimeSpectraKeys.lambda_array: None,
                                    TimeSpectraKeys.file_index_array: None}

        self._reset_time_spectra_tab()

    def _reset_time_spectra_tab(self):
        self.parent.ui.time_spectra_name_label.setText("N/A")
        self.parent.ui.time_spectra_preview_pushButton.setEnabled(False)

    def populate_list_of_folders_to_combine(self):
        list_of_folders = self.parent.session[SessionKeys.list_working_folders]
        list_of_folders_status = self.parent.session.get(SessionKeys.list_working_folders_status, None)
        raw_data_folders = self.parent.raw_data_folders
        o_table = TableHandler(table_ui=self.parent.ui.combine_tableWidget)
        o_table.remove_all_rows()
        for _row_index, _folder in enumerate(list_of_folders):
            o_table.insert_empty_row(row=_row_index)

            # use or not that row
            check_box = QCheckBox()
            if list_of_folders_status is None:
                status = False
            else:
                status = list_of_folders_status[_row_index]
            check_box.setChecked(status)
            o_table.insert_widget(row=_row_index,
                                  column=0,
                                  widget=check_box,
                                  centered=True)
            check_box.clicked.connect(self.parent.radio_buttons_of_folder_changed)

            # number of images in that folder
            nbr_files = raw_data_folders[_folder]['nbr_files']
            o_table.insert_item(row=_row_index,
                                column=1,
                                value=nbr_files,
                                editable=False)

            # full path of the folder
            o_table.insert_item(row=_row_index,
                                column=2,
                                value=_folder,
                                editable=False)

    def update_list_of_folders_to_use(self):
        o_table = TableHandler(table_ui=self.parent.ui.combine_tableWidget)
        nbr_row = o_table.row_count()
        list_of_folders_to_use = []
        list_of_folders_to_use_status = []
        for _row_index in np.arange(nbr_row):
            _horizontal_widget = o_table.get_widget(row=_row_index,
                                                    column=0)
            radio_button = _horizontal_widget.layout().itemAt(1).widget()
            if radio_button.isChecked():
                list_of_folders_to_use.append(o_table.get_item_str_from_cell(row=_row_index,
                                                                             column=2))
                status = True
            else:
                status = False
            list_of_folders_to_use_status.append(status)

        self.parent.session[SessionKeys.list_working_folders_status] = list_of_folders_to_use_status

        self.logger.info("Updating list of folders to use:")
        self.logger.info(f"{list_of_folders_to_use}")

        # check or load the selected rows
        loading_worked = True
        for _folder_name, _folder_status in zip(list_of_folders_to_use, list_of_folders_to_use_status):
            if _folder_status:
                if self.parent.raw_data_folders[_folder_name]['data'] is None:
                    loading_worked = self.load_that_folder(folder_name=_folder_name)

                # load time spectra if not already there
                if self.parent.time_spectra['file_name'] is None:
                    self.load_time_spectra_file(folder=_folder_name)

    def load_time_spectra_file(self, folder=None):
        """
        load the time spectra file
        :param folder: location of the time spectra file
        :return:
        """
        o_time_spectra = GetTimeSpectraFilename(parent=self.parent,
                                                folder=folder)
        full_path_to_time_spectra = o_time_spectra.retrieve_file_name()

        o_time_handler = TimeSpectraHandler(parent=self.parent,
                                            time_spectra_file_name=full_path_to_time_spectra)
        o_time_handler.load()
        o_time_handler.calculate_lambda_scale()

        tof_array = o_time_handler.tof_array
        lambda_array = o_time_handler.lambda_array
        file_index_array = np.arange(len(tof_array))

        self.parent.time_spectra[TimeSpectraKeys.file_name] = full_path_to_time_spectra
        self.parent.time_spectra[TimeSpectraKeys.tof_array] = tof_array
        self.parent.time_spectra[TimeSpectraKeys.lambda_array] = lambda_array
        self.parent.time_spectra[TimeSpectraKeys.file_index_array] = file_index_array
        self.parent.time_spectra[TimeSpectraKeys.counts_array] = o_time_handler.counts_array

        # update time spectra tab
        self.parent.ui.time_spectra_name_label.setText(os.path.basename(full_path_to_time_spectra))
        self.parent.ui.time_spectra_preview_pushButton.setEnabled(True)

    def load_that_folder(self, folder_name=None):
        """
        this routine load all the images of the selected folder
        :param folder_name: full path of the folder containing the images to load
        :return: True if the loading worked, False otherwise
        """
        if not os.path.exists(folder_name):
            self.logger.info(f"Unable to load data from folder {folder_name}")
            return False

        # load the data
        o_load = LoadFiles(parent=self.parent,
                           folder=folder_name)
        data = o_load.retrieve_data()
        self.parent.raw_data_folders[folder_name]['data'] = data

        return True
