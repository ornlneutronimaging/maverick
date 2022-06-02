import os
from qtpy.QtWidgets import QFileDialog, QCheckBox
import logging
import numpy as np

from ..utilities.file_handler import FileHandler
from ..utilities.table_handler import TableHandler
from ..utilities.time_spectra import GetTimeSpectraFilename, TimeSpectraHandler
from ..utilities import TimeSpectraKeys
from ..utilities.get import Get
from ..session import SessionKeys
from ..load.load_files import LoadFiles
from .combine import Combine
from ..utilities import CombineAlgorithm, TimeSpectraKeys


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

    def refresh_table_clicked(self):
        self.logger.info("User clicked the refresh table!")
        top_folder = self.parent.session[SessionKeys.top_folder]
        list_folders = FileHandler.get_list_of_folders(top_folder)
        # checking if there is any new folder
        current_list_of_folders = self.parent.session[SessionKeys.list_working_folders]
        for _folder in list_folders:
            if not (_folder in current_list_of_folders):
                self.parent.session[SessionKeys.list_working_folders].append(_folder)
                self.parent.session[SessionKeys.list_working_folders_status].append(False)

                list_files = FileHandler.get_list_of_files(_folder)
                nbr_files = len(list_files)
                data = {'data': None,
                        'list_files': list_files,
                        'nbr_files': nbr_files}
                self.parent.raw_data_folders[_folder] = data
                self.insert_row_entry(_folder)

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
        o_table = TableHandler(table_ui=self.parent.ui.combine_tableWidget)
        o_table.remove_all_rows()
        for _folder in list_of_folders:
            self.insert_row_entry(folder=_folder)

    def insert_row_entry(self, folder=None):
        list_of_folders_status = self.parent.session.get(SessionKeys.list_working_folders_status, None)
        raw_data_folders = self.parent.raw_data_folders

        o_table = TableHandler(table_ui=self.parent.ui.combine_tableWidget)
        row = o_table.row_count()
        o_table.insert_empty_row(row=row)

        # use or not that row
        check_box = QCheckBox()
        if list_of_folders_status is None:
            status = False
        else:
            status = list_of_folders_status[row]
        check_box.setChecked(status)
        o_table.insert_widget(row=row,
                              column=0,
                              widget=check_box,
                              centered=True)
        check_box.clicked.connect(self.parent.radio_buttons_of_folder_changed)

        # number of images in that folder
        nbr_files = raw_data_folders[folder]['nbr_files']
        o_table.insert_item(row=row,
                            column=1,
                            value=nbr_files,
                            editable=False)

        # full path of the folder
        o_table.insert_item(row=row,
                            column=2,
                            value=folder,
                            editable=False)

    def update_list_of_folders_to_use(self, force_recalculation_of_time_spectra=False):
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

        for _folder_name in list_of_folders_to_use:

            if force_recalculation_of_time_spectra:
                self.load_time_spectra_file(folder=_folder_name)

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

    def combine_algorithm_changed(self):
        o_get = Get(parent=self.parent)
        combine_algorithm = o_get.combine_algorithm()
        self.parent.session[SessionKeys.combine_algorithm] = combine_algorithm
        self.logger.info(f"Algorithm to combine changed to: {combine_algorithm}")
        self.combine_folders()
        self.display_profile()

    def combine_folders(self):
        o_combine = Combine(parent=self.parent)
        o_combine.run()

    def combine_roi_changed(self):
        live_combine_image = self.parent.live_combine_image
        image_view = self.parent.combine_image_view
        roi_item = self.parent.combine_roi_item_id

        region = roi_item.getArraySlice(live_combine_image,
                                        image_view.imageItem)
        x0 = region[0][0].start
        x1 = region[0][0].stop - 1
        y0 = region[0][1].start
        y1 = region[0][1].stop - 1

        width = x1 - x0
        height = y1 - y0

        self.parent.session[SessionKeys.combine_roi] = [x0, y0, width, height]

    def display_profile(self):
        combine_data = self.parent.combine_data
        [x0, y0, width, height] = self.parent.session[SessionKeys.combine_roi]

        o_get = Get(parent=self.parent)
        combine_algorithm = o_get.combine_algorithm()
        time_spectra_x_axis_name = o_get.combine_x_axis_selected()

        if combine_algorithm == CombineAlgorithm.mean:
            profile_signal = [np.mean(_data[y0:y0+height, x0:x0+width]) for _data in combine_data]
        elif combine_algorithm == CombineAlgorithm.median:
            profile_signal = [np.median(_data[y0:y0+height, x0:x0+width]) for _data in combine_data]
        else:
            raise NotImplementedError("Combine algorithm not implemented!")

        self.parent.combine_profile_view.clear()
        x_axis = self.parent.time_spectra[time_spectra_x_axis_name]
        self.parent.combine_profile_view.plot(x_axis, profile_signal, pen='r', symbol='x')
        self.parent.combine_profile_view.setLabel("left", f"{combine_algorithm} counts")
        self.parent.combine_profile_view.setLabel("bottom", time_spectra_x_axis_name)
