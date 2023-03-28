from .ClassAbstracts import System
from ..tools.systems_registers_tools import is_valid_channel


class OutputConditioning(System):
    r"""
Output Conditioning Channel - Offset and Scaling
System ID: 0xD0 through 0xdF

+---------------------+------+-------------+--------------------+-------------+---------+------------------------+
| Register Name       | Id   | Type        | Unit               | Range       | Default | Comment                |
+=====================+======+=============+====================+=============+=========+========================+
|                     |      |             |                    |             |         |                        |
+---------------------+------+-------------+--------------------+-------------+---------+------------------------+
    """

    # TODO: Not implemented yet in firmware
    @staticmethod
    def help():
        print(OutputConditioning.__doc__)

    def __init__(self, channel: int = 0, board=None):
        self.sys_id = 0xD0 | channel
        self._readonly = False

        self.gain = {'id': self.sys_id << 8 | 0x00,
                     'type': float,
                     'unit': None,
                     'range': None,
                     'default': 0,
                     'value': 0}
        self.offset = {'id': self.sys_id << 8 | 0x01,
                       'type': bool,
                       'unit': None,
                       'range': None,
                       'default': 1,
                       'value': 1}
        System.__init__(self, channel, board)
        self.name = self.__class__.__name__
        if not is_valid_channel(self._channel):
            raise ValueError('Channel Range Error')