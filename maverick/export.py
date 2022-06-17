from qtpy.QtWidgets import QFileDialog
import logging

from .session import SessionKeys


class Export:

    def __init__(self, parent=None):
        self.parent = parent
        self.logger = logging.getLogger("maverick")

    def run(self):
        working_dir = self.parent.session[SessionKeys.top_folder]
        _folder = str(QFileDialog.getExistingDirectory(caption="Select Folder to Export the Images",
                                                       directory=working_dir,
                                                       options=QFileDialog.ShowDirsOnly))

        if _folder == "":
            self.logger.info("User cancel export images!")
            return

        self.logger.info(f"Combined and Binned images will be exported to {_folder}!")
