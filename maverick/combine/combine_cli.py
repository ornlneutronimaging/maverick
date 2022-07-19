from PIL import Image
import numpy as np
from tqdm import tqdm
import glob
import os
import shutil
from pathlib import Path
from PIL.TiffTags import TAGS_V2 as TIFFTAGS_V2

from utilities.file_handler import FileHandler


class CombineCLI:

    def __init__(self, list_of_folders):
        folder_list_of_files_dict = CombineCLI.retrieve_list_of_files(list_of_folders)
        self.spectra_file = CombineCLI.get_spectra_file(list_of_folders[0])
        self.data_3d, self.metadata_array = CombineCLI.load_list_of_files(folder_list_of_files_dict)

    def run(self, algorithm):
        if algorithm == 'mean':
            self.data_2d = np.mean(self.data_3d, axis=0)
        elif algorithm == 'median':
            self.data_2d = np.median(self.data_3d, axis=0)
        else:
            raise NotImplementedError(f"algorithm {algorithm} not implemented!")

    def export(self, output_folder=None):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # time stamp
        new_short_file_name = str(Path(output_folder) / "image_Spectra.txt")
        shutil.copy(self.spectra_file, new_short_file_name)

        # data
        [nbr_files_to_create, height, width] = np.shape(self.data_2d)
        for file_index in tqdm(range(nbr_files_to_create)):
            _output_file_name = str(Path(output_folder) / f"image_{file_index:04d}.tif")
            _data = self.data_2d[file_index][:]
            _metadata = self.metadata_array[file_index]
            image = Image.fromarray(_data)
            image.save(_output_file_name, tiffinfo=_metadata)

    @staticmethod
    def get_spectra_file(folder_name):
        time_spectra = glob.glob(folder_name + "/*_Spectra.txt")
        if time_spectra and os.path.exists(time_spectra[0]):
            return time_spectra[0]
        return ""

    @staticmethod
    def load_list_of_files(folder_list_of_files_dict):

        data_3d = []
        metadata_array = []

        list_of_keys = list(folder_list_of_files_dict.keys())

        for _index in tqdm(range(len(list_of_keys))):
            _folder = list_of_keys[_index]
            list_of_files = folder_list_of_files_dict[_folder]

            data_array = []
            for _file_index in tqdm(range(len(list_of_files))):
                _file = list_of_files[_file_index]
                metadata_data_dict = CombineCLI.get_tiff_data(_file)
                if _index == 0:
                    metadata_array.append(metadata_data_dict['metadata'])
                data_array.append(metadata_data_dict['data'])
            data_3d.append(data_array)

        return data_3d, metadata_array

    @staticmethod
    def retrieve_list_of_files(list_of_folders):
        """
        create a dictionary of keys being the folder name, value being the list of files in this folder

        :param list_of_folders:
        :return: dictionary
        """
        if len(list_of_folders) < 2:
            raise ValueError("At least 2 folders are needed!")

        folder_list_of_files_dict = {}
        nbr_files_in_folder = -1
        for _folder_index in tqdm(range(len(list_of_folders))):
            _folder = list_of_folders[_folder_index]
            list_of_tif = FileHandler.get_list_of_tif(_folder)
            if nbr_files_in_folder == -1:
                nbr_files_in_folder = len(list_of_tif)
            else:
                if nbr_files_in_folder != len(list_of_tif):
                    raise ValueError("Folders do not have the same amount of files!")
                elif nbr_files_in_folder == 0:
                    raise ValueError(f"Folders {_folder} is empty!")

            folder_list_of_files_dict[_folder] = list_of_tif

        return folder_list_of_files_dict

    @staticmethod
    def get_tiff_data(filename):
        _o_image = Image.open(filename)

        # metadata
        metadata = CombineCLI.parse_tiff_header(_o_image)

        # image
        data = np.array(_o_image)
        _o_image.close()

        return {'metadata': metadata,
                'data': data}


    @staticmethod
    def parse_tiff_header(tiff_image):
        """Returns the tag from a TIFF image (loaded by PIL) in human readable dict."""
        return dict(tiff_image.tag_v2)