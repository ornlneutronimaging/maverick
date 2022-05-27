import os

from .log.log_launcher import LogHandler
from .utilities.get import Get
from .session.load_previous_session_launcher import LoadPreviousSessionLauncher
from .session.session_handler import SessionHandler


class EventHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def check_log_file_size(self):
        o_handler = LogHandler(parent=self.parent,
                               log_file_name=self.parent.log_file_name)
        o_handler.cut_log_size_if_bigger_than_buffer()

    def automatically_load_previous_session(self):
        o_get = Get(parent=self.parent)
        full_config_file_name = o_get.automatic_config_file_name()
        if os.path.exists(full_config_file_name):
            load_session_ui = LoadPreviousSessionLauncher(parent=self.parent)
            load_session_ui.show()
        else:
            o_session = SessionHandler(parent=self.parent)
            self.session_dict = o_session.session
