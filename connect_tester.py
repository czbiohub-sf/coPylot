import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import custom_sliders


class MainTestWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title = "Hello World"
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()

    def initUI(self):  # Window properties are set in the initUI() method
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(10, 10, 10, 10)

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(-100)
        slider.setMaximum(100)
        slider.setValue(0)
        slider.setTickPosition(slider.TicksBelow)
        slider.setTickInterval(1)

        layout.addWidget(slider)

        lcd = QLCDNumber()
        lcdMonitor = QLCDNumber()

        spinbox = QDoubleSpinBox()
        spinbox.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        spinbox.setDecimals(2)
        spinbox.setSizeIncrement(0.1, 0.1)
        spinbox.setRange(-1.0, 1.0)
        spinbox.setValue(0.3)
        spinbox.setMaximumSize(52, 27)

        layout.addWidget(spinbox)
        layout.addWidget(lcd)
        layout.addWidget(lcdMonitor)

        slider.valueChanged.connect(lcd.display)
        slider.valueChanged.connect(spinbox.setValue)
        spinbox.valueChanged.connect(slider.setValue)

        float_slider = custom_sliders.QDoubleSlider(2)
        float_slider.setMaximum(1.0)
        float_slider.setMinimum(-1.0)
        float_slider.setValue(-0.9)
        layout.addWidget(float_slider)

        #float_slider.valueChanged.connect(spinbox.setValue)
        spinbox.valueChanged.connect(float_slider.setValue)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainTestWindow()
    sys.exit(app.exec())
