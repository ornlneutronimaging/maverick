from qtpy.QtWidgets import QFileDialog
import logging
import numpy as np

from .session import SessionKeys
from .utilities.get import Get
from .utilities import TimeSpectraKeys


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

        # use the combined data array
        combine_arrays = self.parent.combine_data

        # retrieve the bin currently selected [[0],[1],[2,3],....]
        o_get = Get(parent=self.parent)
        bins_dict = o_get.current_bins_activated()
        number_of_bins = len(bins_dict[TimeSpectraKeys.file_index_array])

        # initialize progress bar
        self.parent.eventProgress.setMinimum(0)
        self.parent.eventProgress.setMaximum(number_of_bins-1)
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        sample_position = self.parent.session[SessionKeys.sample_position]

        # for loop
        for _index, _bin in enumerate(bins_dict[TimeSpectraKeys.file_index_array]):

            print(f"_bin: {_bin}")

        # define name of combined image using infos
        #   bin range (micro and angstroms)
        #   sample distance



        # Use NeuNorm to export those data (maybe)
            self.parent.eventProgress.setValue(_index+1)

        self.parent.eventProgress.setVisible(False)
