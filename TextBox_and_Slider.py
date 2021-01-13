import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import custom_sliders


class InitializeSliderTextB(QWidget):
    def __init__(self, parent, widget_name, min_range, max_range, data_type, increment, default=0):
        super(QWidget, self).__init__(parent)

        self.increment = increment
        self.default = default
        self.data_type = data_type
        self.max_range = max_range
        self.min_range = min_range
        self.widget_name = widget_name

        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()

        #  label widget
        widget_label = QLabel(self.widget_name)
        print(self.data_type)
        #  text box widget
        widget_textbox = QSpinBox() if (self.data_type == int) else QDoubleSpinBox()

        widget_textbox.setSizeIncrement(self.increment, self.increment)
        widget_textbox.setRange(self.min_range, self.max_range)
        widget_textbox.setValue(self.default)
        widget_textbox.setMaximumSize(52, 27)

        #  slider widget 
        widget_slider = QSlider(Qt.Horizontal)
        widget_slider.setMaximum(self.max_range)
        widget_slider.setMinimum(self.min_range)
        widget_slider.setValue(self.default)

        #  synchronize text box and slider widget values
        widget_slider.valueChanged.connect(widget_textbox.setValue)
        widget_textbox.valueChanged.connect(widget_slider.setValue)

        #  add label and spinbox as widgets in horizontal child layout
        layout.addWidget(widget_label, 1, Qt.AlignRight)
        layout.addWidget(widget_textbox, 1, Qt.AlignLeft)
        layout.addWidget(widget_slider, 1, Qt.AlignLeft)

        self.setLayout(layout)

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dataInWidget = InitializeSliderTextB(None, "testWidget", -100, 100, int, 1, 10)
    sys.exit(app.exec())
