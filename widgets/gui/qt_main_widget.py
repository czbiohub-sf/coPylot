from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from widgets.gui.qt_left_window import LeftWindow
from widgets.gui.qt_live_control import LiveControl
from widgets.gui.qt_timelapse_control import TimelapseControl


class MainWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        self.parent = parent
        self.button_state = False

        # initialize layouts
        self.window_layout = QHBoxLayout()
        self.right_window_layout = QVBoxLayout()

        # Right window
        self.live_window = LiveControl(self, "Live")
        self.timelapse_window = TimelapseControl(self, "Timelapse")

        self.right_window_layout.addWidget(self.live_window)
        self.right_window_layout.addWidget(self.timelapse_window)

        # left window
        self.left_window = LeftWindow(self)
        self.window_layout.addWidget(self.left_window)

        # right window
        self.window_layout.addLayout(self.right_window_layout)

        self.setLayout(self.window_layout)

    @pyqtSlot()
    def toggle_disabled(self):
        """
        function to disable all input widgets when button to enter timelapse mode is pressed
        """
        self.button_state = not self.button_state

        self.left_window.toggle_button.setDisabled(self.button_state)

        self.timelapse_window.view_combobox.setDisabled(self.button_state)
        self.timelapse_window.laser_combobox.setDisabled(self.button_state)
        self.live_window.setDisabled(self.button_state)

        for parameter_object in self.left_window.parameter_objects:
            parameter_object.spinbox.setDisabled(self.button_state)
            parameter_object.slider.setDisabled(self.button_state)
