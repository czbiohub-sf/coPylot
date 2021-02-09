from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qt_live_control
import qt_parameters_widget
from widgets.gui import qt_timelapse_control


class ModeWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        self.parent = parent
        self.button_state = False

        self.layout = QVBoxLayout()

        self.live_window = qt_live_control.LiveControl(self, "Live")
        self.timelapse_window = qt_timelapse_control.TimelapseControl(self, "Timelapse")

        self.layout.addWidget(self.live_window)
        self.layout.addWidget(self.timelapse_window)

        self.setLayout(self.layout)

    @pyqtSlot()
    def toggle_state(self):
        """
        function to disable all input widgets when button to enter timelapse mode is pressed
        """
        self.button_state = not self.button_state

        self.timelapse_window.view_combobox.setDisabled(self.button_state)
        self.timelapse_window.laser_combobox.setDisabled(self.button_state)
        self.live_window.setDisabled(self.button_state)

        for parameter_object in self.parent.parameters_widget.parameter_objects:
            parameter_object.spinbox.setDisabled(self.button_state)
            parameter_object.slider.setDisabled(self.button_state)

