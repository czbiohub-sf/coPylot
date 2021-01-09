import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QCheckBox, QVBoxLayout, QWidget, \
    QHBoxLayout, QComboBox, QDateEdit, QDateTimeEdit, QDial, QDoubleSpinBox, QFontComboBox, QLCDNumber, QLineEdit, \
    QProgressBar, QRadioButton, QSlider, QSpinBox, QTimeEdit
from PyQt5.QtCore import *
from PyQt5.QtGui import *


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

        # label = QLabel("My name is Luke")
        # label.setAlignment(Qt.AlignHCenter)
        # self.setCentralWidget(label)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(10,10,10,10)
        
        label = QLabel()
        label.setText("Luke's UI")
        font = label.font()
        font.setPointSize(30)
        label.setFont(font)
        label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(label)

        checkbox = QCheckBox("select for profits!")
        layout.addWidget(checkbox)

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(10)
        slider.setMaximum(30)
        slider.setValue(20)
        slider.setTickPosition(slider.TicksBelow)
        slider.setTickInterval(1)
        layout.addWidget(slider)

        textbox = QLineEdit("add your text here")
        layout.addWidget(textbox)

        widget = QWidget()  # QWidget() acts as a container for the laid out widgets - base class for all widgets
        widget.setLayout(layout)

        self.setCentralWidget(widget)

        self.show()  # not shown by default


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainTestWindow()
    # app.exec()  # must come last
    sys.exit(app.exec())  # "sys.exit(n) quits your application and returns n to the parent process (normally your
    # shell), then other parts of the system can detect when your program exited due to an error"

# https://www.learnpyqt.com/tutorials/creating-your-first-window/
# libxcb-xinerama0
