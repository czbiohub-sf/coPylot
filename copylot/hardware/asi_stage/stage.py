import serial
from enum import Enum


class ASIStageScanMode(Enum):
    """
    0 for raster, 1 for serpentine
    """
    RASTER = 0
    SERPENTINE = 1


class ASIStageException(Exception):
    pass


class ASIStage:
    """
    ASIStage

    Parameters
    ----------
    com_port : str

    """

    def __init__(self, com_port: str = None):
        self.com_port = com_port if com_port else "COM6"

        self.ser = serial.Serial(self.com_port)
        print(self.ser.name)

    def __del__(self):
        self.ser.close()

    def set_speed(self, speed):
        message = f"speed x={speed}\r"
        print("set speed to scan: " + message)
        self.ser.write(message)

    def set_default_speed(self, speed):
        message = "speed x=10 y=10\r"
        print("set speed to scan: " + message)
        self.ser.write(message)

    def set_backlash(self):
        message = "backlash x=0.04 y=0.0\r"
        print("set backlash: " + message)
        self.ser.write(message)

    def set_scan_mode(self, mode: ASIStageScanMode = ASIStageScanMode.RASTER):
        """
        Method to set scan mode.

        Parameters
        ----------
        mode : ASIStageScanMode

        """
        message = f"scan f={mode}\r"
        print(message)
        self.ser.write(message)

    def zero(self):
        """
        Set current position to zero.
        """
        message = f"zero\r"
        print(message)
        self.ser.write(message)

    def start_scan(self):
        message = "scan"
        print(message)
        self.ser.write(message)

    def scanr(self, x=0, y=0):
        message = f"scanr x={x} y={y}"
        print(message)
        self.ser.write(message)

    def scanv(self, x=0, y=0, f=1.0):
        message = f"scanv x={x} y={y} f={f}"
        print(message)
        self.ser.write(message)
