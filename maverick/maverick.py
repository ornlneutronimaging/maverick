from qtpy import QtCore
from qtpy.QtWidgets import QApplication, QMainWindow
import sys
import os
import logging
import warnings

warnings.filterwarnings("ignore")

from .utilities.get import Get
from .utilities.config_handler import ConfigHandler
from .utilities import TimeSpectraKeys
from .utilities.time_spectra import TimeSpectraLauncher
from .log.log_launcher import LogLauncher
from .event_hander import EventHandler
from .session import session
from .session.session_handler import SessionHandler
from .session import SessionKeys
from .initialization import Initialization
from .utilities.check import Check
from .combine.event_handler import EventHandler as CombineEventHandler

from . import load_ui


class MainWindow(QMainWindow):
    session = session  # dictionary that will keep record of the entire UI and used to load and save the session
    log_id = None  # ui id of the log QDialog
    version = None   # current version of application

    # raw_data_folders = {'full_path_to_folder1': {'data': [image1, image2, image3...],
    #                                              'list_files': [file1, file2, file3,...],
    #                                              'nbr_files': 0,
    #                                              },
    #                     'full_path_to_folder2': {'data': [image1, image2, image3...],
    #                                              'list_files': [file1, file2, file3,...],
    #                                              'nbr_files': 0,
    #                                              },
    #                     ....
    #                    }
    raw_data_folders = None  # dictionary of data for each of the folders

    # combine_data = [image1, image2, image3...]
    combine_data = None

    # time spectra file and arrays
    time_spectra = {TimeSpectraKeys.file_name: None,
                    TimeSpectraKeys.tof_array: None,
                    TimeSpectraKeys.lambda_array: None,
                    TimeSpectraKeys.file_index_array: None}

    # pyqtgraph view
    combine_image_view = None  # combine image view id - top right plot
    combine_profile_view = None  # combine profile plot view id - bottom right plot
    bin_profile_view = None  # bin profile
    combine_roi_item_id = None  # pyqtgraph item id of the roi (combine tab)
    combine_file_index_radio_button = None  # in combine view
    tof_radio_button = None  # in combine view
    lambda_radio_button = None  # in combine view
    live_combine_image = None  # live combine image used by ROI

    def __init__(self, parent=None):
        """
        Initialization
        Parameters
        ----------
        """
        super(MainWindow, self).__init__(parent)
        self.ui = load_ui('mainWindow.ui', baseinstance=self)
        self.initialization()
        self.setup()
        self.setWindowTitle(f"maverick - v{self.version}")

    def initialization(self):
        o_init = Initialization(parent=self)
        o_init.all()

    def setup(self):
        """
        This is taking care of
            - initializing the session dict
            - setting up the logging
            - retrieving the config file
            - loading or not the previous session
        """
        o_config = ConfigHandler(parent=self)
        o_config.load()

        current_folder = None
        if self.config['debugging']:
            list_homepath = self.config['homepath']
            for _path in list_homepath:
                if os.path.exists(_path):
                    current_folder = _path
            if current_folder is None:
                current_folder = os.path.expanduser('~')
        else:
            current_folder = os.path.expanduser('~')
        self.session[SessionKeys.top_folder] = current_folder

        o_get = Get(parent=self)
        log_file_name = o_get.log_file_name()
        version = o_get.version()
        self.version = version
        self.log_file_name = log_file_name
        logging.basicConfig(filename=log_file_name,
                            filemode='a',
                            format='[%(levelname)s] - %(asctime)s - %(message)s',
                            level=logging.INFO)
        logger = logging.getLogger("maverick")
        logger.info("*** Starting a new session ***")
        logger.info(f" Version: {version}")

        o_event = EventHandler(parent=self)
        o_event.automatically_load_previous_session()

    # Menu
    def session_load_clicked(self):
        o_session = SessionHandler(parent=self)
        o_session.load_from_file()
        o_session.load_to_ui()

    def session_save_clicked(self):
        o_session = SessionHandler(parent=self)
        o_session.save_from_ui()
        o_session.save_to_file()

    def help_log_clicked(self):
        LogLauncher(parent=self)

    # widgets events
    def select_top_folder_button_clicked(self):
        o_event = CombineEventHandler(parent=self)
        o_event.select_top_folder()

    def refresh_table_clicked(self):
        o_event = CombineEventHandler(parent=self)
        o_event.refresh_table_clicked()

    def radio_buttons_of_folder_changed(self):
        o_event = CombineEventHandler(parent=self)
        o_event.update_list_of_folders_to_use()
        o_event.combine_folders()
        o_event.display_profile()

    def time_spectra_preview_clicked(self):
        TimeSpectraLauncher(parent=self)

    def combine_algorithm_changed(self):
        o_event = CombineEventHandler(parent=self)
        o_event.combine_algorithm_changed()

    def combine_roi_changed(self):
        o_event = CombineEventHandler(parent=self)
        o_event.combine_roi_changed()

    def closeEvent(self, event):
        o_session = SessionHandler(parent=self)
        o_session.save_from_ui()
        o_session.automatic_save()

        o_event = Check(parent=self)
        o_event.log_file_size()

        logging.info(" #### Leaving maverick ####")
        self.close()

    def mouse_moved_in_combine_image_preview(self):
        """Mouse moved in the combine pyqtgraph image preview (top right)"""
        pass


def main(args):
    app = QApplication(args)
    app.setStyle("Fusion")
    app.aboutToQuit.connect(clean_up)
    app.setApplicationDisplayName("maverick")
    # app.setWindowIcon(PyQt4.QtGui.QIcon(":/icon.png"))
    application = MainWindow()
    application.show()
    sys.exit(app.exec_())


def clean_up():
    app = QApplication.instance()
    app.closeAllWindows()
