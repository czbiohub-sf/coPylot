import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class DefineNumberTimepointsWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()

        #  create exposure widget as label and QDoubleSpinBox
        nb_timepoints_label = QLabel("nb_timepoints")
        nb_timepoints_input = QSpinBox()
        nb_timepoints_input.setSizeIncrement(1, 1)
        nb_timepoints_input.setRange(0, 1000)
        nb_timepoints_input.setValue(600)
        nb_timepoints_input.setMaximumSize(52, 27)

        #  add label and spinbox as widgets in horizontal child layout
        layout.addWidget(nb_timepoints_label, 1, Qt.AlignRight)
        layout.addWidget(nb_timepoints_input, 1, Qt.AlignLeft)

        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    timepointsWidget = DefineNumberTimepointsWidget()
    sys.exit(app.exec())
