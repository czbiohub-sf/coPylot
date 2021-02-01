import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qt_microscope_mode_control
import qt_left_window


class MainWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        self.parent = parent
        self.button_state = False
        self.parameter_values = []  # to hold parameter values sent from left window. To be fetched on button press

        # initialize layouts
        self.window_layout = QHBoxLayout()
        self.right_window_layout = QVBoxLayout()

        # Right window
        self.view_window = qt_microscope_mode_control.MicroscopeModeControl(self, "Live")
        self.timelapse_window = qt_microscope_mode_control.MicroscopeModeControl(self, "Timelapse", True, True)

        self.right_window_layout.addWidget(self.view_window)
        self.right_window_layout.addWidget(self.timelapse_window)

        # left window
        self.left_window = qt_left_window.LeftWindow(self)
        self.window_layout.addWidget(self.left_window)

        # right window
        self.window_layout.addLayout(self.right_window_layout)

        self.setLayout(self.window_layout)

    @pyqtSlot()
    def toggle_state(self):
        """
        slot decorated function to disable all input widgets when button to enter timelapse mode is pressed
        """
        self.button_state = not self.button_state
        for j in range(1, self.timelapse_window.layout.count()):
            if j != 1:
                self.timelapse_window.layout.itemAt(j).widget().setDisabled(self.button_state)

        self.window_layout.itemAt(0).widget().setDisabled(self.button_state)

    def receive_parameter_val(self):  #
        print("received in main widget")
        self.view_window.launch_nidaq_instance(self.parameter_values)
