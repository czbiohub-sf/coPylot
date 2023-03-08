class System:
    _is_a_system = False

    def __init__(self, channel: int or None = None, board=None):
        self.name = self.__class__.__name__
        self._channel = channel
        self._is_a_system = True
        if channel is None:
            self._is_a_system = False
        self._board = board
        self.register_list = self._get_register_list()

    # TODO: this would run faster without lookup loop, just send hex to board.set/get
    def set_register(self, register_name_or_id: str or int, value,
                     set_internal: bool = False, cmd_delay: float = None):
        if self._board is not None:
            if isinstance(register_name_or_id, int):
                reg_id = register_name_or_id
                register_name = [item[0] for item in self.register_list if item[1]['id'] & 0x0f == reg_id][0]
            else:
                register_name = register_name_or_id
            reg = self.__dict__[register_name]
            if reg['type'] is float:
                value = float(value)
            response = self._board.set_value(reg, value, cmd_delay=cmd_delay)
            if isinstance(value, list):
                value = value[0]
            if set_internal:
                self.__dict__[register_name]['value'] = value
            return response
        return None

    def get_register(self, register_name_or_id: str or int):
        if self._board is not None:
            if isinstance(register_name_or_id, int):
                reg_id = register_name_or_id
                register_name = [item[0] for item in self.register_list if item[1]['id'] & 0x0f == reg_id][0]
            else:
                register_name = register_name_or_id
            response = self._board.get_value(self.__dict__[register_name])

            return response
        return None

    def get_register_names(self):
        return [item for item in self.__dict__ if type(self.__dict__[item]) is dict]

    def _get_register_list(self):
        return [[item, self.__dict__[item]] for item in self.__dict__ if type(self.__dict__[item]) is dict]


class InputStage(System):
    _is_a_system = False

    def __init__(self, channel: int or None = 0, board=None):
        System.__init__(self, channel, board)
        self.name = self.__class__.__name__

    def SetAsInput(self):
        ch = self._board.channel[self._channel]
        ch.Manager.set_register('input', self)


class ControlStage(System):
    _is_a_system = False

    def __init__(self, channel: int or None = 0, board=None):
        System.__init__(self, channel, board)
        self.name = self.__class__.__name__

    def SetAsControlMode(self):
        ch = self._board.channel[self._channel]
        ch.Manager.set_register('control', self)