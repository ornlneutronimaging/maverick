import os
from qtpy.QtWidgets import QFileDialog, QCheckBox
import logging

from ..utilities.file_handler import FileHandler
from ..utilities.table_handler import TableHandler
from ..session import SessionKeys


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

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
        o_table = TableHandler(table_ui=self.parent.ui.combine_tableWidget)
        o_table.remove_all_rows()
        for _row_index, _folder in enumerate(list_of_folders):
            o_table.insert_empty_row(row=_row_index)

            check_box = QCheckBox()
            o_table.insert_widget(row=_row_index,
                                  column=0,
                                  widget=check_box,
                                  centered=True)
            o_table.insert_item(row=_row_index,
                                column=1,
                                value=_folder,
                                editable=False)
