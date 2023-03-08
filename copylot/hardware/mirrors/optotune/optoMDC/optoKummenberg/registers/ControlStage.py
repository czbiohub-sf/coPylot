from .ClassAbstracts import ControlStage
from ..tools.systems_registers_tools import is_valid_channel


class CurrentFeedThrough(ControlStage):
    r"""
Control Mode Channel - Offset and Scaling
System ID: 0xB0 through 0xB7

+---------------------+------+-------------+--------------------+-------------+---------+------------------------+
| Register Name       | Id   | Type        | Unit               | Range       | Default | Comment                |
+=====================+======+=============+====================+=============+=========+========================+
|feed_through_enabled | 0x00 |             | None               |             | 0       |                        |
+---------------------+------+-------------+--------------------+-------------+---------+------------------------+

    """

    @staticmethod
    def help():
        print(FeedThrough.__doc__)

    def __init__(self, channel: int = 0, board=None):
        self.sys_id = 0xB0 | channel
        self._readonly = False

        self.feed_through_enabled = {'id': self.sys_id << 8 | 0x00,
                                     'type': bool,
                                     'unit': 'Hz',
                                     'range': [True, False],
                                     'default': 0,
                                     'value': 0}
        ControlStage.__init__(self, channel, board)
        self.name = self.__class__.__name__
        if not is_valid_channel(self._channel):
            raise ValueError('Channel Range Error')

