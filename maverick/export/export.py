from qtpy.QtWidgets import QFileDialog
import logging
import os
import inflect

from NeuNorm.normalization import Normalization

from ..session import SessionKeys
from ..utilities.get import Get
from ..utilities import TimeSpectraKeys
from .utilities import create_output_file_name
from ..bin.statistics import Statistics
from ..utilities.status_message_config import StatusMessageStatus, show_status_message


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

        file_index_array = bins_dict[TimeSpectraKeys.file_index_array]
        tof_array = bins_dict[TimeSpectraKeys.tof_array]
        lambda_array = bins_dict[TimeSpectraKeys.lambda_array]

        o_statistics = Statistics(parent=self.parent)
        self.logger.info(f"Images will be exported in: {_folder}")

        # for loop
        number_of_file_created = 0
        for _index, _bin in enumerate(file_index_array):

            self.logger.info(f"bin #: {_bin}")

            if _bin == []:
                self.logger.info(f"-> empty bin, skipping.")
                self.parent.eventProgress.setValue(_index + 1)
                continue

            # define name of combined image using infos
            #   bin range (micro and angstroms)
            #   sample distance
            output_file_name = create_output_file_name(folder=_folder,
                                                       bin_index=_index,
                                                       sample_position=sample_position,
                                                       list_file_index=_bin,
                                                       list_tof=tof_array[_index],
                                                       list_lambda=lambda_array[_index])

            self.logger.info(f"-> output_file_name: {output_file_name}")
            number_of_file_created += 1

            # we combine the file listed in _bin using the method
            _data_dict = o_statistics.extract_data_for_this_bin(list_runs=_bin)
            full_image = _data_dict['full_image']
            o_norm = Normalization()
            o_norm.load(data=full_image)
            o_norm.data['sample']['file_name'][0] = os.path.basename(output_file_name)
            o_norm.export(folder=_folder, data_type='sample', file_type='tiff')

        # Use NeuNorm to export those data (maybe)
            self.parent.eventProgress.setValue(_index+1)

        self.parent.eventProgress.setVisible(False)
        p = inflect.engine()
        self.logger.info(f"Done exporting {number_of_file_created} " + p.plural("file", number_of_file_created) + "!")
        show_status_message(parent=self.parent,
                            message=f"Export to folder {_folder} ... Done!",
                            status=StatusMessageStatus.ready,
                            duration_s=5)
