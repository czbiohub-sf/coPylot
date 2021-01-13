from PyQt5.QtWidgets import QSlider


class QDoubleSlider(QSlider):

    def __init__(self, decimals):
        super().__init__()

        self.decimals = decimals
        self._max_int = 10 ** self.decimals

        super().setMinimum(0)
        super().setMaximum(self._max_int)

        # initialize
        self._min_value = 0.0
        self._max_value = 1.0

    @property
    def _value_range(self):
        return self._max_value - self._min_value

    def value(self):
        return float(super().value() / self._max_int)

    def setValue(self, value):
        super().setValue(int(value * self._max_int))

    def setMinimum(self, value):
        if value > self._max_value:
            raise ValueError("Minimum limit cannot be higher than maximum")

        super().setMinimum(int(value * self._max_int))

    def setMaximum(self, value):
        if value < self._min_value:
            raise ValueError("Minimum limit cannot be higher than maximum")

        super().setMaximum(int(value * self._max_int))

    def minimum(self):
        return self._min_value

    def maximum(self):
        return self._max_value
