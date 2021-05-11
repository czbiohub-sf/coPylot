from math import log10
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtWidgets import (
    QWidget,
    QSlider,
    QLineEdit,
    QLabel,
    QSpinBox,
    QDoubleSpinBox,
    QAbstractSpinBox,
)


class TextboxAndSlider(QWidget):
    def __init__(
        self,
        parent,
        widget_name,
        data_type,
        increment,
        row,
        json_defaults,
    ):
        super(QWidget, self).__init__(parent)

        self.json_defaults = json_defaults
        self.val = self.json_defaults["parameters"][widget_name][0]
        self.min = self.json_defaults["parameters"][widget_name][1]
        self.max = self.json_defaults["parameters"][widget_name][2]

        self.parent = parent
        self.widget_name = widget_name
        self.data_type = data_type
        self.increment = increment
        self.row = row

        self.range_visible = False  # state tracker for visibility of range input lines

        # widgets accessed by slot member functions
        self.slider = QSlider(Qt.Horizontal)
        self.slider.mouseReleaseEvent = self.mouseReleaseEvent

        self.min_input_line = QLineEdit()
        self.max_input_line = QLineEdit()

        self.label = QLabel(self.widget_name)

        self.num_decimals = -log10(self.increment)
        self._max_int = 10 ** self.num_decimals

        # set spinbox type and connection based on data type
        if self.data_type == int:
            self.spinbox = QSpinBox()
            self.slider_scaling = (
                1  # makes scaling in self.slider parameter have no effect
            )

            #  synchronize text box and self.slider widget values
            self.slider.valueChanged.connect(self.spinbox.setValue)
            self.spinbox.valueChanged.connect(self.slider.setValue)

        elif self.data_type == float:
            self.spinbox = QDoubleSpinBox()
            self.spinbox.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
            self.spinbox.setDecimals(self.num_decimals)

            self.slider_scaling = (
                self._max_int
            )  # scale self.slider parameters into integer range

            self.slider.valueChanged.connect(self.int_to_scaled_float)
            self.spinbox.valueChanged.connect(self.float_to_scaled_int)

        else:
            raise TypeError("Only integers or floats acceptable for QSpinBox objects")

        # set parameters unaffected by datatype
        # set ranges
        self.spinbox.setRange(self.min, self.max)
        self.slider.setMaximum(self.max * self.slider_scaling)
        self.slider.setMinimum(self.min * self.slider_scaling)

        # set values
        self.spinbox.setValue(self.val)
        self.slider.setValue(self.val * self.slider_scaling)

        self.min_input_line.setText(str(self.min))
        self.max_input_line.setText(str(self.max))

        self.spinbox.setSizeIncrement(self.increment, self.increment)

        self.spinbox.setFixedSize(75, 27)
        self.min_input_line.setMaximumSize(66, 24)
        self.max_input_line.setMaximumSize(66, 24)

        self.min_input_line.editingFinished.connect(self.update_min_range)
        self.max_input_line.editingFinished.connect(self.update_max_range)

        self.parent.grid_layout.addWidget(self.label, self.row, 0)
        self.parent.grid_layout.addWidget(self.spinbox, self.row, 1)
        self.parent.grid_layout.addWidget(self.slider, self.row, 2, 1, 3)

        # added here to prevent trigger on startup
        self.spinbox.editingFinished.connect(
            self.parent.parent.live_widget.launch_nidaq
        )

    @pyqtSlot()
    def toggle_range_widgets(self):
        self.range_visible = not self.range_visible
        if self.range_visible:
            self.parent.grid_layout.removeWidget(self.slider)
            self.parent.grid_layout.addWidget(self.min_input_line, self.row, 2)
            self.parent.grid_layout.addWidget(self.slider, self.row, 3)
            self.parent.grid_layout.addWidget(self.max_input_line, self.row, 4)

        elif not self.range_visible:
            self.parent.grid_layout.removeWidget(self.slider)
            self.min_input_line.setParent(None)
            self.max_input_line.setParent(None)
            self.parent.grid_layout.addWidget(self.slider, self.row, 2, 1, 3)

    @pyqtSlot()
    def update_min_range(self):
        min_text = self.min_input_line.text()  # fetch QLineEdit contents

        try:
            min_text = float(min_text)  # if a number, convert to float
            if min_text > self.max:
                self.min_input_line.setText(
                    str(self.min)
                )  # reset to last acceptable min range
            else:
                self.min = min_text
                self.spinbox.setRange(self.min, self.max)

                if self.data_type == int:
                    self.slider.setMinimum(self.min)
                elif self.data_type == float:
                    self.slider.setMinimum(self.min * self._max_int)
        except ValueError:
            self.min_input_line.setText("NaN")

    @pyqtSlot()
    def update_max_range(self):
        max_text = self.max_input_line.text()
        try:
            max_text = float(max_text)
            if max_text < self.min:
                self.max_input_line.setText(str(self.max))
            else:
                self.max = max_text
                self.spinbox.setRange(self.min, self.max)

                if self.data_type == int:
                    self.slider.setMaximum(self.max)
                elif self.data_type == float:
                    self.slider.setMaximum(self.max * self._max_int)
        except ValueError:
            self.max_input_line.setText("NaN")

    @pyqtSlot(float)
    def float_to_scaled_int(self, value):
        self.slider.setValue(int(value * self._max_int))

    @pyqtSlot(int)
    def int_to_scaled_float(self, value):
        self.spinbox.setValue(float(value / self._max_int))

    def mouseReleaseEvent(self, event):
        self.parent.parent.live_widget.launch_nidaq()

    @property
    def range(self):
        return [float(self.min_input_line.text()), float(self.max_input_line.text())]
