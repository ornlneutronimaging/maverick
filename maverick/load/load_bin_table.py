from qtpy.QtWidgets import QFileDialog
import logging
import json

from ..session import SessionKeys


class LoadBinTable:

    def __init__(self, parent=None):
        self.parent = parent
        self.logger = logging.getLogger("maverick")

    def run(self):
        working_dir = self.parent.session[SessionKeys.top_folder]
        bin_table = QFileDialog.getOpenFileName(caption="Select table bin",
                                                directory=working_dir,
                                                filter="table bin (*.json)")

        bin_table_file_name = bin_table[0]
        if not bin_table_file_name:
            self.logger.info("User cancel loading bin file!")
            return

        with open(bin_table_file_name, 'r') as json_file:
            table = json.load(json_file)
        print(table)