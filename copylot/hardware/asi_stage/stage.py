import serial
from enum import IntEnum


class ASIStageScanMode(IntEnum):
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

        self.serial_connection = serial.Serial()
        self.serial_connection.port = self.com_port
        self.serial_connection.baudrate = 9600
        self.serial_connection.parity = serial.PARITY_NONE
        self.serial_connection.bytesize = serial.EIGHTBITS
        self.serial_connection.stopbits = serial.STOPBITS_ONE
        self.serial_connection.xonoff = False
        self.serial_connection.rtscts = False
        self.serial_connection.dsrdtr = False
        self.serial_connection.write_timeout = 1
        self.serial_connection.timeout = 1

        self.serial_connection.set_buffer_size(12800, 12800)
        self.serial_connection.open()

        if self.serial_connection.is_open:
            self.serial_connection.reset_input_buffer()
            self.serial_connection.reset_output_buffer()

        print(self.serial_connection.name)

    def __del__(self):
        self.serial_connection.close()

    def set_speed(self, speed):
        message = f"speed x={speed}\r"
        print("set speed to scan: " + message)
        self.serial_connection.write(message.encode())

    def set_default_speed(self, speed):
        message = "speed x=10 y=10\r"
        print("set speed to scan: " + message)
        self.serial_connection.write(message.encode())

    def set_backlash(self):
        message = "backlash x=0.04 y=0.0\r"
        print("set backlash: " + message)
        self.serial_connection.write(message.encode())

    def set_scan_mode(self, mode: ASIStageScanMode = ASIStageScanMode.RASTER):
        """
        Method to set scan mode.

        Parameters
        ----------
        mode : ASIStageScanMode

        """
        message = f"scan f={int(mode)}\r"
        print(message)
        self.serial_connection.write(message.encode())

    def zero(self):
        """
        Set current position to zero.
        """
        message = f"zero\r"
        print(message)
        self.serial_connection.write(message.encode())

    def start_scan(self):
        message = "scan"
        print(message)
        self.serial_connection.write(message.encode())

    def scanr(self, x=0, y=0):
        message = f"scanr x={x} y={y}"
        print(message)
        self.serial_connection.write(message.encode())

    def scanv(self, x=0, y=0, f=1.0):
        message = f"scanv x={x} y={y} f={f}"
        print(message)
        self.serial_connection.write(message.encode())
