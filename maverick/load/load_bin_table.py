from qtpy.QtWidgets import QFileDialog
import logging

from ..session import SessionKeys


class LoadBinTable:

    def __init__(self, parent=None):
        self.parent = parent
        self.logger = logging.getLogger("maverick")

    def run(self):
        working_dir = self.parent.session[SessionKeys.top_folder]
        (bin_table_file, extension) = str(QFileDialog.getOpenFileName(caption="Select table bin",
                                                  directory=working_dir,
                                                  filter="table bin (*.json)"))

        if not bin_table_file:
            self.logger.info("User cancel loading bin file!")
            return





