from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSlider, QWidget, QVBoxLayout, QDoubleSpinBox, QLabel
from PyQt5.QtCore import pyqtSignal


class DoubleSlider(QSlider):
    # create our our signal that we can connect to if necessary
    doubleValueChanged = pyqtSignal(float)

    def __init__(self, decimals=5, *args, **kargs):
        super(DoubleSlider, self).__init__(*args, **kargs)
        self._multi = 10**decimals

        self.valueChanged.connect(self.emitDoubleValueChanged)

    def emitDoubleValueChanged(self):
        value = float(super(DoubleSlider, self).value()) / self._multi
        self.doubleValueChanged.emit(value)

    def value(self):
        return float(super(DoubleSlider, self).value()) / self._multi

    def setMinimum(self, value):
        return super(DoubleSlider, self).setMinimum(int(value * self._multi))

    def setMaximum(self, value):
        return super(DoubleSlider, self).setMaximum(int(value * self._multi))

    def setSingleStep(self, value):
        return super(DoubleSlider, self).setSingleStep(value * self._multi)

    def singleStep(self):
        return float(super(DoubleSlider, self).singleStep()) / self._multi

    def setValue(self, value):
        super(DoubleSlider, self).setValue(int(value * self._multi))
