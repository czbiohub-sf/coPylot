import serial


class FilterWheel:
    """
    FilterWheel

    Parameters
    ----------
    com_port : str

    """

    def __init__(self, com_port: str = None):
        self.com_port = com_port if com_port else "COM8"

        self.serial_connection = serial.Serial()
        self.serial_connection.port = self.com_port
        self.serial_connection.baudrate = 9600

        print(self.serial_connection.name)