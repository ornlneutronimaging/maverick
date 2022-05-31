import os
from qtpy.QtWidgets import QFileDialog, QCheckBox
import logging
import numpy as np

from ..utilities.file_handler import FileHandler
from ..utilities.table_handler import TableHandler
from ..session import SessionKeys


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

        # get list of folders in top folder
        self.parent.session[SessionKeys.top_folder] = os.path.abspath(_folder)
        list_folders = FileHandler.get_list_of_folders(_folder)
        self.parent.session[SessionKeys.list_working_folders] = list_folders
        self.parent.ui.top_folder_label.setText(_folder)

        # display list of folders in widget + in second column use or not radiobutton
        self.populate_list_of_folders_to_combine()

    def populate_list_of_folders_to_combine(self):
        list_of_folders = self.parent.session[SessionKeys.list_working_folders]
        list_of_folders_status = self.parent.session.get(SessionKeys.list_working_folders_status, None)
        o_table = TableHandler(table_ui=self.parent.ui.combine_tableWidget)
        o_table.remove_all_rows()
        for _row_index, _folder in enumerate(list_of_folders):
            o_table.insert_empty_row(row=_row_index)

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
            o_table.insert_item(row=_row_index,
                                column=1,
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
                                                                             column=1))
                status = True
            else:
                status = False
            list_of_folders_to_use_status.append(status)

        self.parent.session[SessionKeys.list_working_folders_status] = list_of_folders_to_use_status

        self.logger.info("Updating list of folders to use:")
        self.logger.info(f"{list_of_folders_to_use}")

