import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from math import log10


class InitializeSliderTextB(QWidget):
    def __init__(self, parent, widget_name, min_range, max_range, data_type, increment, default=0):
        super(QWidget, self).__init__(parent)

        self.widget_name = widget_name
        self.max_range = max_range
        self.min_range = min_range
        self.data_type = data_type
        self.increment = increment
        self.default = default

        self.numDecimals = -log10(self.increment)
        self._max_int = 10 ** self.numDecimals

        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        layout.setSpacing(3)
        layout.setContentsMargins(0, 0, 0, 0)

        @pyqtSlot(float)
        def floatToScaledInt(value):
            slider.setValue(int(value * self._max_int))

        @pyqtSlot(int)
        def intToScaledFloat(value):
            spinbox.setValue(float(value / self._max_int))

        #  parameter name widget
        label = QLabel(self.widget_name)

        #  slider widget 
        slider = QSlider(Qt.Horizontal)

        #  set widget parameters and whether to use custom slots based on data type
        if self.data_type == int:
            spinbox = QSpinBox()
            slider.setMaximum(self.max_range)
            slider.setMinimum(self.min_range)
            slider.setValue(self.default)
            
            #  synchronize text box and slider widget values
            slider.valueChanged.connect(spinbox.setValue)
            spinbox.valueChanged.connect(slider.setValue)

        elif self.data_type == float:
            spinbox = QDoubleSpinBox()
            spinbox.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
            spinbox.setDecimals(self.numDecimals)

            # scale inputs to integer range based on number of decimal points of smallest increment
            slider.setMaximum(self.max_range * self._max_int)
            slider.setMinimum(self.min_range * self._max_int)
            slider.setValue(self.default * self._max_int)

            #  synchronize text box and slider widget values
            slider.valueChanged.connect(intToScaledFloat)
            spinbox.valueChanged.connect(floatToScaledInt)

        else:
            raise TypeError("Only integers or floats acceptable for Spinbox objects")

        #  set universal spinbox parameters
        spinbox.setSizeIncrement(self.increment, self.increment)
        spinbox.setRange(self.min_range, self.max_range)
        spinbox.setValue(self.default)
        #spinbox.setMaximumSize(80, 27)
        spinbox.setFixedSize(65, 27)

        # layout to hold slider and spinbox for alignment with one another
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(spinbox, 1, Qt.AlignRight)
        controls_layout.addWidget(slider, 1, Qt.AlignRight)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(5)

        #  add widgets / layouts in horizontal child layout
        layout.addWidget(label, 1, Qt.AlignLeft)
        layout.addLayout(controls_layout)

        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dataInWidget = InitializeSliderTextB(None, "testWidget", -100, 100, int, 1, 10)
    sys.exit(app.exec())
