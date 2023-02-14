from enum import Enum

# TODO - where should vendor specific SDK imports live?
# See https://github.com/alliedvision/VimbaPython for more details on downloading Vimba (unfortunately not on PyPi)
from vimba import *

from copylot.hardware.cameras.abstract_camera import AbstractCamera


class AVTCameraException(Exception):
    pass


class BinningMode(Enum):
    AVERAGE = "Average"
    SUM = "Sum"
