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

        self.ser = serial.Serial()
        self.ser.port = self.com_port
        self.ser.baudrate = 9600
        self.ser.parity = serial.PARITY_NONE
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.xonoff = False
        self.ser.rtscts = False
        self.ser.dsrdtr = False
        self.ser.write_timeout = 1
        self.ser.timeout = 1

        self.ser.set_buffer_size(12800, 12800)
        self.ser.open()

        if self.ser.is_open:
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()

        print(self.ser.name)

    def __del__(self):
        self.ser.close()

    def set_speed(self, speed):
        message = f"speed x={speed}\r"
        print("set speed to scan: " + message)
        self.ser.write(message.encode())

    def set_default_speed(self):
        message = "speed x=10 y=10\r"
        print("set speed to scan: " + message)
        self.ser.write(message.encode())

    def set_backlash(self):
        message = "backlash x=0.04 y=0.0\r"
        print("set backlash: " + message)
        self.ser.write(message.encode())

    def set_scan_mode(self, mode: ASIStageScanMode = ASIStageScanMode.RASTER):
        """
        Method to set scan mode.

        Parameters
        ----------
        mode : ASIStageScanMode

        """
        message = f"scan f={int(mode)}\r"
        print(message)
        self.ser.write(message.encode())

    def zero(self):
        """
        Set current position to zero.
        """
        message = f"zero\r"
        print(message)
        self.ser.write(message.encode())

    def start_scan(self):
        message = "scan"
        print(message)
        self.ser.write(message.encode())

    def scanr(self, x=0, y=0):
        message = f"scanr x={x} y={y}"
        print(message)
        self.ser.write(message.encode())

    def scanv(self, x=0, y=0, f=1.0):
        message = f"scanv x={x} y={y} f={f}"
        print(message)
        self.ser.write(message.encode())

    def info_x(self):
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

        command = "INFO x"
        message = bytes(f"{command}\r", encoding="ascii")
        print(message)
        self.ser.write(message)
        response = self.ser.readline()
        response = response.decode(encoding="ascii")
        print(response)
        print(f"Recv: {response.strip()}")

        response = self.ser.readline()
        response = response.decode(encoding="ascii")
        print(response)
        print(f"Recv: {response.strip()}")

        response = self.ser.readline()
        response = response.decode(encoding="ascii")
        print(response)
        print(f"Recv: {response.strip()}")

        response = self.ser.readline()
        response = response.decode(encoding="ascii")
        print(response)
        print(f"Recv: {response.strip()}")
