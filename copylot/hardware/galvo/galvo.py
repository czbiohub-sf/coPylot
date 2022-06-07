from copylot.hardware.ni_daq.live_nidaq import LiveNIDaq


class Galvo:
    speed: float = 0.5

    def __init__(self, name: str):
        self.name = name
        self.daq = LiveNIDaq()
        self.channel =

    @staticmethod
    def _pos2voltage(pos: float):
        """ TODO: implement this properly.

        Parameters
        ----------
        pos

        Returns
        -------

        """
        return pos

    def scan(self):
        raise NotImplementedError

    def set_speed(self, s: float):
        self.speed = s

    def set_minimum(self, min: float):
        raise NotImplementedError

    def set_maximum(self, max: float):
        raise NotImplementedError

    def set_position(self, pos: float):
        self.daq.set_constant_voltage(self.channel, self._pos2voltage(pos))
