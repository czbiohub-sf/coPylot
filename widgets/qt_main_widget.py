import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qt_view_laser_mode
import qt_left_window


class MainWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        self.button_state = False

        # initialize layouts
        self.window_layout = QHBoxLayout()
        self.right_window_layout = QVBoxLayout()

        # Right window
        self.view_window = qt_view_laser_mode.InitializeComboButton(self, "View")
        self.timelapse_window = qt_view_laser_mode.InitializeComboButton(self, "Timelapse", True, True)

        self.right_window_layout.addWidget(self.view_window)
        self.right_window_layout.addWidget(self.timelapse_window)

        self.window_layout.addWidget(qt_left_window.left_window(self))  # left window
        self.window_layout.addLayout(self.right_window_layout)

        self.setLayout(self.window_layout)

    @pyqtSlot()
    def toggleState(self):
        """
        slot decorated function to disable all input widgets when button to enter timelapse mode is pressed
        """
        self.button_state = not self.button_state
        for j in range(1, self.timelapse_window.layout.count()):
            if j != 1:
                self.timelapse_window.layout.itemAt(j).widget().setDisabled(self.button_state)

        self.window_layout.itemAt(0).widget().setDisabled(self.button_state)
