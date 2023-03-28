from .ClassAbstracts import System
from ..tools.systems_registers_tools import is_valid_channel


class InputConditioning(System):
    r"""
Input Conditioning Channel - Offset and Scaling
System ID: 0x98 through 0x9f

+----------------+------+-------------+--------------------+-------------+---------+------------------------+
| Register Name  | Id   | Type        | Unit               | Range       | Default | Comment                |
+================+======+=============+====================+=============+=========+========================+
| gain           | 0x00 | float 32-bit|                    |             | 1.0     |                        |
+----------------+------+-------------+--------------------+-------------+---------+------------------------+
| offset         | 0x01 | float 32-bit|                    |             | 0.0     |                        |
+----------------+------+-------------+--------------------+-------------+---------+------------------------+

    """

    @staticmethod
    def help():
        print(InputConditioning.__doc__)

    def __init__(self, channel: int = 0, board=None):
        self.sys_id = 0x98 | channel
        self._readonly = False

        self.gain = {'id': self.sys_id << 8 | 0x00,
                     'type': float,
                     'unit': None,
                     'range': None,
                     'default': 1,
                     'value': 1}

        self.offset = {'id': self.sys_id << 8 | 0x01,
                       'type': float,
                       'unit': None,
                       'range': None,
                       'default': 0,
                       'value': 0}
        System.__init__(self, channel, board)
        self.name = self.__class__.__name__
        if not is_valid_channel(self._channel):
            raise ValueError('Channel Range Error')

    def SetGain(self, value):
        return self.set_register('gain', value)

    def SetOffset(self, value):
        return self.set_register('offset', value)

    def GetGain(self):
        return self.get_register('gain')

    def GetOffset(self):
        return self.get_register('offset')