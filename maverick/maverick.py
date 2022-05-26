from qtpy import QtCore
from qtpy.QtWidgets import QApplication, QMainWindow
import sys
import os
import logging
import warnings
warnings.filterwarnings("ignore")

from . import load_ui


class MainWindow(QMainWindow):


    def __init__(self, parent=None):
        """
        Initialization
        Parameters
        ----------
        """
        # Base class
        super(MainWindow, self).__init__(parent)

        self.ui = load_ui('mainWindow.ui', baseinstance=self)
        # self.init_interface()

        # configuration of config
        # o_get = Get(parent=self)
        # log_file_name = o_get.get_log_file_name()
        # self.log_file_name = log_file_name
        # logging.basicConfig(filename=log_file_name,
        #                     filemode='a',
        #                     format='[%(levelname)s] - %(asctime)s - %(message)s',
        #                     level=logging.INFO)
        # logging.info("*** Starting a new session ***")
        # #logging.info(f" Version: {versioneer.get_versions()}")
        # logging.info(f" Version: FIXME!")




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
