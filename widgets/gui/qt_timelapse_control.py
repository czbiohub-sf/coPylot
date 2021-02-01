from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qt_line_break
from widgets.hardware.control import NIDaq


class TimelapseControl(QWidget):
    def __init__(self, parent, button_name):
        super(QWidget, self).__init__(parent)

        self.parent = parent
        self.button_name = button_name

        self.button_state = False  # allows timelapse mode to be turned off and on
        self.color_tracker = True  # tracker to set new background color when timelapse mode is on

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        self.layout.addWidget(qt_line_break.LineBreak(Qt.AlignTop))  # line break between live and timelapse

        # add launch button that disables parameter input, preventing input change
        self.section_button = QPushButton(self.button_name)

        self.section_button.pressed.connect(self.parent.toggle_state)
        self.section_button.pressed.connect(self.launch_nidaq_instance)
        self.section_button.pressed.connect(self.button_color_change)

        self.layout.addWidget(self.section_button)

        # placeholders for future selection options
        self.view_combobox = QComboBox()
        self.view_combobox.addItem("view 1")
        self.view_combobox.addItem("view 2")
        self.layout.addWidget(self.view_combobox)

        self.laser_combobox = QComboBox()
        self.laser_combobox.addItem("488")
        self.laser_combobox.addItem("561")
        self.layout.addWidget(self.laser_combobox)

        self.setLayout(self.layout)

    def launch_nidaq_instance(self):
        parameters = self.parent.left_window.update_parameters
        print("launched with: ", parameters)
        # not yet implemented

    def button_color_change(self):
        if self.color_tracker:
            self.section_button.setStyleSheet("background-color: red")
        else:
            self.section_button.setStyleSheet("")
        self.color_tracker = not self.color_tracker

