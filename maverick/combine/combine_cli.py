from maverick.utilities.file_handler import FileHandler


class CombineCLI:

    def __init__(self, list_of_folders):

        if len(list_of_folders) < 2:
            raise ValueError("At least 2 folders are needed!")

        list_of_files = []
        nbr_files_in_folder = -1
        for _folder in list_of_folders:
            list_of_tif = FileHandler.get_list_of_tif(_folder)
            if nbr_files_in_folder == -1:
                nbr_files_in_folder = len(list_of_tif)
            else:
                if nbr_files_in_folder != len(list_of_tif):
                    raise ValueError("Folders do not have the same amount of files!")
                elif nbr_files_in_folder == 0:
                    raise ValueError("Folders is empty!")

            list_of_files.append(list_of_tif)




