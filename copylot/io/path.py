import tempfile
from os import makedirs
from os.path import exists


def get_home_folder():
    """
    Method that returns home folder in the current runtime.

    Returns
    -------
    str

    """
    from pathlib import Path

    home_folder = f"{Path.home()}"
    return home_folder


def get_temp_folder():
    """
    Method that creates a new temp folder and returns
    the path to the created temp folder.

    Returns
    -------
    str

    """
    temp_folder = None

    try:
        temp_folder = tempfile.gettempdir()
        if exists(temp_folder):
            raise FileExistsError
        else:
            makedirs(temp_folder)
    except Exception:
        pass

    return temp_folder
