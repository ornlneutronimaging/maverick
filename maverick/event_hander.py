import os
from qtpy.QtWidgets import QFileDialog
import logging

from .log.log_launcher import LogHandler
from .utilities.file_handler import FileHandler
from .utilities.get import Get
from .session.load_previous_session_launcher import LoadPreviousSessionLauncher
from .session.session_handler import SessionHandler
from .session import SessionKeys


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent
        self.logger = logging.getLogger("maverick")

    def automatically_load_previous_session(self):
        o_get = Get(parent=self.parent)
        full_config_file_name = o_get.automatic_config_file_name()
        if os.path.exists(full_config_file_name):
            load_session_ui = LoadPreviousSessionLauncher(parent=self.parent)
            load_session_ui.show()
        else:
            o_session = SessionHandler(parent=self.parent)
            self.session = o_session.session

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
        print(list_folders)

        # display list of folders in widget + in second column use or not radiobutton
