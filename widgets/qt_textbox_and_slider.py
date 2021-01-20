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

        @pyqtSlot(float)
        def floatToScaledInt(value):
            slider.setValue(int(value * self._max_int))

        @pyqtSlot(int)
        def intToScaledFloat(value):
            spinbox.setValue(float(value / self._max_int))

        @pyqtSlot(float)
        def changeMinRange(value):
            self.min_range = value
            spinbox.setRange(self.min_range, self.max_range)
            if self.data_type == int:
                slider.setMinimum(self.min_range)
            elif self.data_type == float:
                slider.setMinimum(self.min_range * self._max_int)

        @pyqtSlot(float)
        def changeMaxRange(value):
            self.max_range = value
            spinbox.setRange(self.min_range, self.max_range)
            if self.data_type == int:
                slider.setMaximum(self.max_range)
            elif self.data_type == float:
                slider.setMaximum(self.max_range * self._max_int)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        #  parameter name widget
        label = QLabel(self.widget_name)

        #  slider widget 
        slider = QSlider(Qt.Horizontal)

        #  set data-type dependent widget parameters and whether to use custom slots
        if self.data_type == int:
            spinbox = QSpinBox()
            max_input_box = QSpinBox()
            min_input_box = QSpinBox()

            # makes scaling in slider parameter have no effect
            slider_scaler = 1

            #  synchronize text box and slider widget values
            slider.valueChanged.connect(spinbox.setValue)
            spinbox.valueChanged.connect(slider.setValue)

        elif self.data_type == float:
            spinbox = QDoubleSpinBox()
            max_input_box = QDoubleSpinBox()
            min_input_box = QDoubleSpinBox()

            spinbox_list = [spinbox, max_input_box, min_input_box]

            for i in spinbox_list:
                i.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
                i.setDecimals(self.numDecimals)

            # scale slider parameters into integer range
            slider_scaler = self._max_int

            #  synchronize text box and slider widget values
            slider.valueChanged.connect(intToScaledFloat)
            spinbox.valueChanged.connect(floatToScaledInt)

        else:
            raise TypeError("Only integers or floats acceptable for Spinbox objects")

        #  set slider parameters based on data type (by value of slider_scaler)
        #slider_layout = QHBoxLayout()
        slider.setMaximum(self.max_range * slider_scaler)
        slider.setMinimum(self.min_range * slider_scaler)
        slider.setValue(self.default * slider_scaler)

        #slider_layout.addWidget(slider)

        #  set universal spinbox parameters
        spinbox.setSizeIncrement(self.increment, self.increment)
        spinbox.setRange(self.min_range, self.max_range)
        spinbox.setValue(self.default)
        spinbox.setFixedSize(65, 27)

        # addition of a maximum and minimum parameter range input widget
        range_input_layout = QVBoxLayout()
        range_input_layout.setContentsMargins(0, 0, 0, 0)
        range_input_layout.setSpacing(2)

        # define range input spinboxes
        max_range_layout = QHBoxLayout()
        min_range_layout = QHBoxLayout()

        range_layout_list = [min_input_box, max_input_box]  # defined earlier based on input data type

        for i in range_layout_list:
            i.setRange(-100000, 100000)  # beyond realistic range for any parameter
            i.setFixedSize(65, 27)
            i.setSizeIncrement(self.increment, self.increment)

        min_input_box.setValue(self.min_range)
        max_input_box.setValue(self.max_range)

        # add spinboxes with a label to a horizontal box layout

        #max_range_layout.addWidget(QLabel("max range"))
        #max_range_layout.addWidget(max_input_box)
        #min_range_layout.addWidget(QLabel("min range"))
        #min_range_layout.addWidget(min_input_box)

        # add min and max layouts to vertical master layout
        range_input_layout.addLayout(max_range_layout)
        range_input_layout.addLayout(min_range_layout)

        # link change in range spinboxes with slots to change slider and main value input ranges
        min_input_box.valueChanged.connect(changeMinRange)
        max_input_box.valueChanged.connect(changeMaxRange)

        # layout to hold slider and spinbox for alignment with one another
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(spinbox, 1, Qt.AlignHCenter)
        controls_layout.addWidget(min_input_box)
        controls_layout.addWidget(slider, 1, Qt.AlignHCenter)
        controls_layout.addWidget(max_input_box)

        #  add widgets / layouts in horizontal child layout
        layout.addWidget(label, 1, Qt.AlignLeft)
        layout.addLayout(controls_layout)
        #layout.addLayout(range_input_layout)

        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dataInWidget = InitializeSliderTextB(None, "testWidget", -100, 100, int, 1, 10)
    sys.exit(app.exec())
