import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qt_line_break
from widgets.hardware.control import NIDaq


class MicroscopeModeControl(QWidget):
    def __init__(self, parent, button_name, add_line_break=False, can_disable=False):
        super(QWidget, self).__init__(parent)

        self.parent = parent
        self.button_name = button_name
        self.add_line_break = add_line_break
        self.can_disable = can_disable
        self.color_tracker = True

        self.daq_card = 0

        if self.can_disable:
            self.button_state = False

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        if self.add_line_break:
            self.layout.addWidget(qt_line_break.LineBreak(Qt.AlignTop))

        # add labeled button that, if can_disable = True, disables the comboboxes, preventing input change
        self.section_button = QPushButton(self.button_name)
        if self.can_disable:
            self.section_button.clicked.connect(self.parent.toggle_state)

        self.section_button.clicked.connect(self.launch_nidaq_instance)
        self.section_button.clicked.connect(self.button_color_change)

        self.layout.addWidget(self.section_button)

        # placeholders for future selection options
        self.view_combobox = QComboBox()
        self.view_combobox.addItem("view 1")
        self.view_combobox.addItem("view 2")
        self.layout.addWidget(self.view_combobox)

        self.laser_combobox = QComboBox()
        self.laser_combobox.addItem("...Hz laser")
        self.laser_combobox.addItem("...Hz laser")
        self.layout.addWidget(self.laser_combobox)

        self.setLayout(self.layout)

    def launch_nidaq_instance(self, parameters):
        parameters = self.parent.parameter_values
        self.daq_card = NIDaq(*parameters)

    def button_color_change(self):
        if self.color_tracker:
            self.section_button.setStyleSheet("background-color: red")
        else:
            self.section_button.setStyleSheet("")
        self.color_tracker = not self.color_tracker

