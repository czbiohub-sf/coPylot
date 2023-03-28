from .ClassAbstracts import System
from ..tools.systems_registers_tools import is_valid_channel


class LinearOutput(System):
    r"""
Device Functionality - Firmware Status
System ID: 0xE8 through 0xEF

+--------------------+------+-------------+------+-------+---------+--------------------------------------------------+
| Register Name      | Id   | Type        | Unit | Range | Default | Comment                                          |
+====================+======+=============+======+=======+=========+==================================================+
|current_limit       | 0x00 |float 32-bit |None  |       |         |                                                  |
+--------------------+------+-------------+------+-------+---------+--------------------------------------------------+
| channel_number     | 0x01 |uint 32-bit  |None  |       |         |                                                  |
+--------------------+------+-------------+------+-------+---------+--------------------------------------------------+
| output_current     | 0x02 |float 32-bit |None  |       |         |                                                  |
+--------------------+------+-------------+------+-------+---------+--------------------------------------------------+
| avg_limit_period   | 0x03 |uint 32-bit  |None  |       |         |                                                  |
+--------------------+------+-------------+------+-------+---------+--------------------------------------------------+
| avg_limit_sum      | 0x03 |float 32-bit |None  |       |         |                                                  |
+--------------------+------+-------------+------+-------+---------+--------------------------------------------------+
| cooldown_period    | 0x04 |float 32-bit |None  |       |         |                                                  |
+--------------------+------+-------------+------+-------+---------+--------------------------------------------------+
| min_integral       | 0x05 |float 32-bit |None  |       |         |                                                  |
+--------------------+------+-------------+------+-------+---------+--------------------------------------------------+

    """

    @staticmethod
    def help():
        print(LinearOutput.__doc__)

    _is_a_system = False

    def __init__(self, channel: int = 0, board=None):
        self.sys_id = 0xE8 | channel

        self.current_limit = {'id': self.sys_id << 8 | 0x00,
                              'type': float,
                              'unit': None,
                              'range': None,
                              'default': 0.7,
                              'value': None}
        self.channel_number = {'id': self.sys_id << 8 | 0x01,
                               'type': int,
                               'unit': None,
                               'range': None,
                               'default': None,
                               'value': None}
        self.output_current = {'id': self.sys_id << 8 | 0x02,
                               'type': float,
                               'unit': None,
                               'range': None,
                               'default': None,
                               'value': None}
        self.avg_limit_period = {'id': self.sys_id << 8 | 0x03,
                                 'type': float,
                                 'unit': 'Seconds',
                                 'range': None,
                                 'default': 0.1,
                                 'value': 0.1}
        self.avg_limit_sum = {'id': self.sys_id << 8 | 0x04,
                              'type': float,
                              'unit': None,
                              'range': None,
                              'default': 0.3,
                              'value': 0.3}
        self.cooldown_period = {'id': self.sys_id << 8 | 0x05,
                                'type': float,
                                'unit': 'Seconds',
                                'range': None,
                                'default': 10.0,
                                'value': 10.0}
        System.__init__(self, channel, board)
        self.name = self.__class__.__name__
        if not is_valid_channel(self._channel):
            raise ValueError('Channel Range Error')

    def SetCurrentLimit(self, value):
        return self.set_register('current_limit', value)

    def GetCurrentLimit(self):
        return self.get_register('current_limit')

    def GetChannelNumber(self):
        return self.get_register('channel_number')

    def GetOutputCurrent(self):
        return self.get_register('output_current')

    def SetAverageLimitPeriod(self, value):
        return self.set_register('avg_limit_period', value)

    def GetAverageLimitPeriod(self):
        return self.get_register('avg_limit_period')

    def SetAverageLimitSum(self, value):
        return self.set_register('avg_limit_sum', value)

    def GetAverageLimitSum(self):
        return self.get_register('avg_limit_sum')

    def SetCooldownPeriod(self, value):
        return self.set_register('cooldown_period')

    def GetCooldownPeriod(self):
        return self.get_register('cooldown_period')