import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class ExposureWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        self.initUI()

    def initUI(self):

        layout = QHBoxLayout()

        #  create exposure widget as label and QDoubleSpinBox
        exposure_label = QLabel("exposure")
        exposure_input = QDoubleSpinBox()
        exposure_input.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
        exposure_input.setRange(0.001, 1)
        exposure_input.setDecimals(3)
        exposure_input.setValue(0.02)
        exposure_input.setMaximumSize(60, 27)

        #  add label and spinbox as widgets in horizontal child layout
        layout.addWidget(exposure_label, 1, Qt.AlignRight)
        layout.addWidget(exposure_input, 1, Qt.AlignLeft)

        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    exposureWidget = ExposureWidget()
    sys.exit(app.exec())
