import serial


class ASIStageException(Exception):
    pass


class ASIStage:
    def __init__(self, com_port=None):
        self.com_port = com_port if com_port else "COM6"

        self.ser = serial.Serial('/dev/ttyUSB0')
        print(self.ser.name)

    def __del__(self):
        self.ser.close()

    def set_speed(self, speed):
        message = f"speed x={speed}\r"
        print("set speed to scan: " + message)
        self.ser.write(message)

    def set_backlash(self):
        message = "backlash x=0.04 y=0.0\r"
        print("set backlash: " + message)
        self.ser.write(message)

    def set_scan_mode(self, mode: int = 0):
        """
        Method to set scan mode.

        Parameters
        ----------
        mode : int
            0 for raster, 1 for serpantine

        """
        message = f"scan f={mode}\r"
        print(message)
        self.ser.write(message)
