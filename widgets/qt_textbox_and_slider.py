import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from math import log10
import custom_sliders


class InitializeSliderTextB(QWidget):
    def __init__(self, parent, widget_name, min_range, max_range, data_type, increment, default=0):
        super(QWidget, self).__init__(parent)

        self.widget_name = widget_name
        self.max_range = max_range
        self.min_range = min_range
        self.data_type = data_type
        self.increment = increment
        self.default = default

        # self.slider widget
        self.slider = custom_sliders.DoubleClickableSlider(self)

        # initialize layouts
        self.layout = QHBoxLayout()
        self.controls_layout = QHBoxLayout()

        if self.data_type == int:
            self.spinbox = QSpinBox()
            self.max_input_box = QSpinBox()
            self.min_input_box = QSpinBox()

        elif self.data_type == float:
            self.spinbox = QDoubleSpinBox()
            self.max_input_box = QDoubleSpinBox()
            self.min_input_box = QDoubleSpinBox()

        self.range_visible = False

        self.numDecimals = -log10(self.increment)
        self._max_int = 10 ** self.numDecimals

        self.initUI()

    def initUI(self):

        @pyqtSlot(float)
        def floatToScaledInt(value):
            self.slider.setValue(int(value * self._max_int))

        @pyqtSlot(int)
        def intToScaledFloat(value):
            self.spinbox.setValue(float(value / self._max_int))

        @pyqtSlot(float)
        def change_min_range(value):
            self.max_input_box.setMinimum(value)
            self.min_range = value
            self.spinbox.setRange(self.min_range, self.max_range)
            if self.data_type == int:
                self.slider.setMinimum(self.min_range)
            elif self.data_type == float:
                self.slider.setMinimum(self.min_range * self._max_int)

        @pyqtSlot(float)
        def change_max_range(value):
            self.min_input_box.setMaximum(value)
            self.max_range = value
            self.spinbox.setRange(self.min_range, self.max_range)
            if self.data_type == int:
                self.slider.setMaximum(self.max_range)
            elif self.data_type == float:
                self.slider.setMaximum(self.max_range * self._max_int)

        # override layout margins
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)

        #  parameter name
        label = QLabel(self.widget_name)

        #  set data-type dependent widget parameters and whether to use custom slots
        if self.data_type == int:
            slider_scaler = 1  # makes scaling in self.slider parameter have no effect

            #  synchronize text box and self.slider widget values
            self.slider.valueChanged.connect(self.spinbox.setValue)
            self.spinbox.valueChanged.connect(self.slider.setValue)

        elif self.data_type == float:
            spinbox_list = [self.spinbox, self.max_input_box, self.min_input_box]

            for i in spinbox_list:
                i.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
                i.setDecimals(self.numDecimals)

            slider_scaler = self._max_int  # scale self.slider parameters into integer range

            self.slider.valueChanged.connect(intToScaledFloat)
            self.spinbox.valueChanged.connect(floatToScaledInt)

        else:
            raise TypeError("Only integers or floats acceptable for self.spinbox objects")

        #  set self.slider parameters based on data type (by value of self.slider_scaler)
        self.slider.setMaximum(self.max_range * slider_scaler)
        self.slider.setMinimum(self.min_range * slider_scaler)
        self.slider.setValue(self.default * slider_scaler)

        #  set universal self.spinbox parameters
        self.spinbox.setSizeIncrement(self.increment, self.increment)
        self.spinbox.setRange(self.min_range, self.max_range)
        self.spinbox.setValue(self.default)
        self.spinbox.setFixedSize(65, 27)

        # set features of range selection self.spinboxes
        range_layout_list = [self.min_input_box, self.max_input_box]  # defined earlier based on input data type

        for i in range_layout_list:
            i.setRange(-100000, 100000)  # beyond realistic range for any parameter
            i.setFixedSize(65, 27)
            i.setSizeIncrement(self.increment, self.increment)

        self.min_input_box.setValue(self.min_range)
        self.max_input_box.setValue(self.max_range)

        # link change in range self.spinboxes with slots to change self.slider and main value input ranges
        self.min_input_box.valueChanged.connect(change_min_range)
        self.max_input_box.valueChanged.connect(change_max_range)

        # layout to hold self.slider and self.spinbox for alignment with one another
        self.controls_layout.addWidget(self.spinbox, 1, Qt.AlignHCenter)
        self.controls_layout.addWidget(self.slider, 1, Qt.AlignHCenter)

        #  add widgets / layouts in horizontal child layout
        self.layout.addWidget(label, 1, Qt.AlignLeft)
        self.layout.addLayout(self.controls_layout)

        self.setLayout(self.layout)

    @pyqtSlot()
    def toggle_range_widgets(self):
        self.range_visible = not self.range_visible
        if self.range_visible:
            self.min_input_box.setParent(None)
            self.max_input_box.setParent(None)
        elif not self.range_visible:
            self.controls_layout.removeWidget(self.slider)
            self.controls_layout.addWidget(self.min_input_box)
            self.controls_layout.addWidget(self.slider, 1, Qt.AlignHCenter)
            self.controls_layout.addWidget(self.max_input_box)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dataInWidget = InitializeSliderTextB(None, "testWidget", -100, 100, int, 1, 10)
    sys.exit(app.exec())
