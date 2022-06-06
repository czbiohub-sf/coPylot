class Laser:
    def __init__(self, wavelength: int = 488, power: int = 0.15):
        self._wavelength = wavelength
        self._power = power

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
