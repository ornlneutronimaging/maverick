from qtpy.QtWidgets import QFileDialog
import os
import logging

from ..utilities.get import Get
from ..session import SessionKeys


class ExportBinTable:

    def __init__(self, parent=None):
        self.parent = parent
        self.logger = logging.getLogger("maverick")

    def run(self):

        working_dir = self.parent.session[SessionKeys.top_folder]
        _folder = str(QFileDialog.getExistingDirectory(caption="Select Folder to ExportImages the Images",
                                                       directory=working_dir,
                                                       options=QFileDialog.ShowDirsOnly))

        if _folder == "":
            self.logger.info("User cancel export bin table!")
            return

        o_get = Get(parent=self.parent)
        current_bin_activated = o_get.current_bins_activated()
        self.logger.info(f"{current_bin_activated} bins table will be exported to {_folder}!")
