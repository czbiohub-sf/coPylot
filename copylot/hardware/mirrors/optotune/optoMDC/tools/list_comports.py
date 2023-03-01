# from optoKummenberg.tools.list_comports import *
from serial.tools import list_ports


def get_mre2_port(hwid='0483:A31E'):
    """str: default hardware id of mre2 board, for port recognition.
    """
    devices = list_ports.comports()
    device = list([device.device for device in devices if hwid in device.hwid])
    return device.pop() if device else None
