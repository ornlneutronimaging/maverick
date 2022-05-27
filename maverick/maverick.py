from qtpy import QtCore
from qtpy.QtWidgets import QApplication, QMainWindow
import sys
import os
import logging
import warnings
warnings.filterwarnings("ignore")

from .utilities.get import Get
from .utilities.config_handler import ConfigHandler
from .log.log_launcher import LogLauncher, LogHandler

from . import load_ui


class MainWindow(QMainWindow):

    session = {'top_folder': None,     # the base folder to start looking at images folder to combine
               'log_buffer_size': 500}

    log_id = None

    def __init__(self, parent=None):
        """
        Initialization
        Parameters
        ----------
        """
        # Base class
        super(MainWindow, self).__init__(parent)

        self.ui = load_ui('mainWindow.ui', baseinstance=self)
        self.setup()

        o_get = Get(parent=self)
        log_file_name = o_get.log_file_name()
        version = o_get.version()
        self.log_file_name = log_file_name
        logging.basicConfig(filename=log_file_name,
                            filemode='a',
                            format='[%(levelname)s] - %(asctime)s - %(message)s',
                            level=logging.INFO)
        logging.info("*** Starting a new session ***")
        logging.info(f" Version: {version}")

    def setup(self):
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

        self.session['top_folder'] = current_folder

    # Menu
    def session_load_clicked(self):
        pass

    def session_save_clicked(self):
        pass

    def help_log_clicked(self):
        LogLauncher(parent=self)


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
