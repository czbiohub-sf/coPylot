import struct
import sys
if sys.platform.startswith('win'):
    print("Spidev is Linux-Only, thus SPI features are disabled.")
else:
    try:
        import spidev
    except ImportError:
        print("Unable to import spidev! Try: pip install spidev")
import time


class SPI:
    def __init__(self, bus: int = 0, device: int = 0):
        self._bus = bus
        self._device = device
        self._spi_comm = spidev.SpiDev()
        self.connect()
        self._spi_comm.max_speed_hz = 125000000//16
        self._spi_comm.mode = 0b01
        self._spi_comm.lsbfirst = False
        self.x_readback = 0
        self.y_readback = 0
        self.reg_value = 0
        self.status = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def set_values(self, system1, register1, system2, register2, data1, data2, data_type='>f'):
        self.send(system1, register1, system2, register2, data1, data2, data_type)
        return self.receive_w()

    def get_values(self, system, register, unit_type):
        resp = self._spi_comm.xfer([0x00, system, register, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        return self.receive_r(resp, unit_type)

    def send(self,  system1, register1, system2, register2, data1, data2, data_type='>f'):
        byte_string = struct.pack('>B', 0) + \
                      struct.pack('>B', 1) + \
                      struct.pack('>B', system1) + \
                      struct.pack('>B', register1) + \
                      struct.pack('>B', system2) + \
                      struct.pack('>B', register2) + \
                      struct.pack(data_type, data1) + \
                      struct.pack(data_type, data2)
        print(byte_string.hex())
        return self._spi_comm.xfer(byte_string)

    # TODO: Test changing pointer location
    def receive_w(self, number_of_bytes: int = 12):
        response = self._spi_comm.readbytes(number_of_bytes)
        status = format(response[0], '08b')
        status_flags = {
            'led_enabled': status[0] is True,
            'linear_drive_enabled': status[1] is True,
            'datalogging_running': status[2] is True,
            'logging_ram_full': status[3] is True,
            'conversation_error': status[4] is True,
            'overtemp_shutdown': status[5] is True,
            'current_b_overlimit': status[6] is True,
            'current_a_overlimit': status[7] is True
        }
        self.status = status_flags
        self.x_readback = struct.unpack('>f', bytes(response[4:8]))[0]
        self.y_readback = struct.unpack('>f', bytes(response[8:12]))[0]

        return status_flags, self.x_readback, self.y_readback

    def receive_r(self, unit_type, number_of_bytes: int = 12):
        response = self._spi_comm.readbytes(number_of_bytes)
        status = format(response[0], '08b')
        status_flags = {
            'led_enabled': status[0] is True,
            'linear_drive_enabled': status[1] is True,
            'datalogging_running': status[2] is True,
            'logging_ram_full': status[3] is True,
            'conversation_error': status[4] is True,
            'overtemp_shutdown': status[5] is True,
            'current_b_overlimit': status[6] is True,
            'current_a_overlimit': status[7] is True
        }
        self.reg_value = struct.unpack(unit_type, bytes(response[0:4]))[0]
        self.x_readback = struct.unpack('>f', bytes(response[4:8]))[0]
        self.y_readback = struct.unpack('>f', bytes(response[8:12]))[0]

        return self.reg_value, self.x_readback, self.y_readback

    def connect(self):
        self._spi_comm.open(self._bus, self._device)

    def disconnect(self):
        self._spi_comm.close()
