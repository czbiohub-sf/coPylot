from os import access, W_OK
from os.path import exists

from copylot.util import get_temp_folder, get_home_folder


def test_home_folder():
    home_folder = get_home_folder()
    print(home_folder)
    assert exists(home_folder)
    assert access(home_folder, W_OK)


def test_temp_folder():
    temp_folder = get_temp_folder()
    print(temp_folder)
    assert exists(temp_folder)
    assert access(temp_folder, W_OK)
