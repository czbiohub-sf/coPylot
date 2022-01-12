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
