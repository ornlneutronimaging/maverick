from PIL import Image
import numpy as np
from tqdm import tqdm

from utilities.file_handler import FileHandler


class CombineCLI:

    def __init__(self, list_of_folders):
        folder_list_of_files_dict = CombineCLI.retrieve_list_of_files(list_of_folders)
        data_3d, metadata_array = CombineCLI.load_list_of_files(folder_list_of_files_dict)

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

        # metadata dict
        try:
            metadata = _o_image.tag_v2.as_dict()
        except AttributeError:
            metadata = None

        # image
        data = np.array(_o_image)
        _o_image.close()

        return {'metadata': metadata,
                'data': data}
