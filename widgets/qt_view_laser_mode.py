import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class InitializeComboButton(QWidget):
    def __init__(self, button_name):
        super(QWidget, self).__init__()
        self.button_name = button_name

        self.initUI()

    def initUI(self):

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(QPushButton(self.button_name))
        layout.addWidget(QComboBox())
        layout.addWidget(QComboBox())

        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    testWidget = InitializeComboButton("test")
    sys.exit(app.exec())
