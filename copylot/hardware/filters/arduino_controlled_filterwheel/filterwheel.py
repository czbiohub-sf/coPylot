import time
import serial


class ArduinoControlledFilterwheel:
    """FilterWheel

    Parameters
    ----------
    com_port : str

    """

    def __init__(self, com_port: str = None):
        self.com_port = com_port if com_port else "COM8"

        self.serial_connection = serial.Serial()
        self.serial_connection.port = self.com_port
        self.serial_connection.baudrate = 1000000
        self.serial_connection.stopbits = serial.STOPBITS_ONE

        self.serial_connection.open()

        print(self.serial_connection.name)

        time.sleep(0.5)

    def __del__(self):
        self.serial_connection.close()

    def _send_message(self, message: str):
        """Send message over serial connection.

        Parameters
        ----------
        message : str

        """
        self.serial_connection.write(bytes(f"{message}\n", encoding="ascii"))

    def _read_response(self) -> str:
        """Receive and read the response from serial communication.

        Returns
        -------
        str

        """
        return self.serial_connection.readline().decode(encoding="ascii")

    def set_position(self, position_index: int):
        """
        Set position of the filterwheel.

        Parameters
        ----------
        position_index : int

        """
        if position_index < 0 or position_index > 5:
            raise ValueError("Bad value for position_index argument...")

        message = f"#s{position_index}"
        self._send_message(message)
        print(self._read_response())
