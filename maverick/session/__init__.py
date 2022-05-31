session = {'top_folder': None,  # the base folder to start looking at images folder to combine
           'list_working_folders': None,  # list of working folders
           'list_working_folders_status': None,  # list of working folders status [True, True, False..]
           'log_buffer_size': 500,   # max size of the log file
           'version': "0.0.1",   # version of that config
           }


class SessionKeys:
    """list of all sessions keys, to easily retrieve them"""

    top_folder = "top_folder"
    list_working_folders = "list_working_folders"
    list_working_folders_status = "list_working_folders_status"
    log_buffer_size = "log_buffer_size"
    version = "version"
