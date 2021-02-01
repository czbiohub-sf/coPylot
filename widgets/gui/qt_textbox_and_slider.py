from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from math import log10


class TextboxAndSlider(QWidget):
    def __init__(self, parent, widget_name, min_range, max_range, data_type, increment, default=0):
        super(QWidget, self).__init__(parent)

        self.widget_name = widget_name
        self.max_range = max_range
        self.min_range = min_range
        self.data_type = data_type
        self.increment = increment
        self.default = default
        self.parent = parent

        self.range_visible = True

        # widgets accessed by slot member functions
        self.slider = QSlider(Qt.Horizontal)
        self.slider.mouseDoubleClickEvent = self.mouseDoubleClickEvent

        self.toggle_button = QPushButton("set range")
        self.min_input_line = QLineEdit()
        self.max_input_line = QLineEdit()

        self.label = QLabel(self.widget_name)

        # initialize layouts
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)

        self.controls_layout = QHBoxLayout()

        self.num_decimals = -log10(self.increment)
        self._max_int = 10 ** self.num_decimals

        # set spinbox type and connection based on data type
        if self.data_type == int:
            self.spinbox = QSpinBox()
            self.slider_scaler = 1  # makes scaling in self.slider parameter have no effect

            #  synchronize text box and self.slider widget values
            self.slider.valueChanged.connect(self.spinbox.setValue)
            self.spinbox.valueChanged.connect(self.slider.setValue)

        elif self.data_type == float:
            self.spinbox = QDoubleSpinBox()
            self.spinbox.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
            self.spinbox.setDecimals(self.num_decimals)

            self.slider_scaler = self._max_int  # scale self.slider parameters into integer range

            self.slider.valueChanged.connect(self.intToScaledFloat)
            self.spinbox.valueChanged.connect(self.floatToScaledInt)

        else:
            raise TypeError("Only integers or floats acceptable for self.spinbox objects")

        #  set universal spinbox parameters
        self.spinbox.setSizeIncrement(self.increment, self.increment)
        self.spinbox.setRange(self.min_range, self.max_range)
        self.spinbox.setValue(self.default)
        self.spinbox.setFixedSize(65, 27)

        #  set slider parameters based on data type (by value of self.slider_scaler)
        self.slider.setMaximum(self.max_range * self.slider_scaler)
        self.slider.setMinimum(self.min_range * self.slider_scaler)
        self.slider.setValue(self.default * self.slider_scaler)

        # set range input default values and connect to update slot
        self.min_input_line.setText(str(self.min_range))
        self.max_input_line.setText(str(self.max_range))

        self.min_input_line.setMaximumSize(46, 18)
        self.max_input_line.setMaximumSize(46, 18)

        self.min_input_line.editingFinished.connect(self.update_min_range)
        self.max_input_line.editingFinished.connect(self.update_max_range)

        # connect button for alternate range input box toggling
        self.toggle_button.pressed.connect(self.toggle_range_widgets)

        # layout to hold self.slider and self.spinbox for alignment with one another
        self.controls_layout.addWidget(self.spinbox, 1, Qt.AlignHCenter)
        self.controls_layout.addWidget(self.slider, 1, Qt.AlignHCenter)
        self.controls_layout.addWidget(self.toggle_button)

        # added here to prevent trigger on startup
        self.spinbox.valueChanged.connect(self.parent.parent.view_window.launch_nidaq_instance)

        #  add widgets / layouts in horizontal child layout
        self.layout.addWidget(self.label, 1, Qt.AlignLeft)
        self.layout.addLayout(self.controls_layout)

        self.setLayout(self.layout)

    @pyqtSlot()
    def toggle_range_widgets(self):
        self.range_visible = not self.range_visible
        if self.range_visible:
            self.min_input_line.setParent(None)
            self.max_input_line.setParent(None)
        elif not self.range_visible:
            self.controls_layout.removeWidget(self.toggle_button)
            self.controls_layout.removeWidget(self.slider)
            self.controls_layout.addWidget(self.min_input_line)
            self.controls_layout.addWidget(self.slider, 1, Qt.AlignHCenter)
            self.controls_layout.addWidget(self.max_input_line)
            self.controls_layout.addWidget(self.toggle_button)

    @pyqtSlot()
    def update_min_range(self):
        min_text = self.min_input_line.text()  # fetch QLineEdit contents
        try:
            min_text = float(min_text)  # if a number, convert to float
            if min_text > self.max_range:
                self.min_input_line.setText(str(self.min_range))  # reset to last acceptable min range
            else:
                self.min_range = min_text
                self.spinbox.setRange(self.min_range, self.max_range)

                if self.data_type == int:
                    self.slider.setMinimum(self.min_range)
                elif self.data_type == float:
                    self.slider.setMinimum(self.min_range * self._max_int)
        except:
            self.min_input_line.setText("NaN")

    @pyqtSlot()
    def update_max_range(self):
        max_text = self.max_input_line.text()
        try:
            max_text = float(max_text)
            if max_text < self.min_range:
                self.max_input_line.setText(str(self.max_range))
            else:
                self.max_range = max_text
                self.spinbox.setRange(self.min_range, self.max_range)

                if self.data_type == int:
                    self.slider.setMaximum(self.max_range)
                elif self.data_type == float:
                    self.slider.setMaximum(self.max_range * self._max_int)
        except:
            self.max_input_line.setText("NaN")
        pass

    @pyqtSlot(float)
    def floatToScaledInt(self, value):
        self.slider.setValue(int(value * self._max_int))

    @pyqtSlot(int)
    def intToScaledFloat(self, value):
        self.spinbox.setValue(float(value / self._max_int))

    def mouseDoubleClickEvent(self, event):
        self.toggle_range_widgets()


