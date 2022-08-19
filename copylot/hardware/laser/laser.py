

class Laser:
    def __init__(self, wavelength: str = "561", power: int = 0.01):
        self._wavelength = wavelength
        self._power = power

    def __del__(self):
        self.turn_off()

    @property
    def wavelength(self):
        return self._wavelength

    @wavelength.setter
    def wavelength(self, wavelength: int):
        raise NotImplementedError

    @property
    def power(self):
        return self._power

    @power.setter
    def power(self, power: int):
        self._power = power

    def turn_on(self):
        pass

    def turn_off(self):
        pass
