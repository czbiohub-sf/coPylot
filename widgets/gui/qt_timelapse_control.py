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

        self.sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.sizePolicy.setHeightForWidth(True)

        self.state_tracker = False  # tracker to set new background color when timelapse mode is on

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        self.layout.addWidget(qt_line_break.LineBreak(Qt.AlignTop))  # line break between live and timelapse

        # add launch button that disables parameter input, preventing input change
        self.section_button = QPushButton(self.button_name)
        #self.section_button.setSizePolicy(self.sizePolicy)

        self.section_button.pressed.connect(self.button_state_change)
        self.section_button.pressed.connect(self.launch_nidaq_instance)

        self.layout.addWidget(self.section_button)

        # placeholders for future selection options
        self.view_combobox = QComboBox()
        self.view_combobox.addItem("view 1")
        self.view_combobox.addItem("view 2")
        self.layout.addWidget(self.view_combobox)

        #self.view_combobox.setSizePolicy(self.sizePolicy)

        self.laser_combobox = QComboBox()
        self.laser_combobox.addItem("488")
        self.laser_combobox.addItem("561")
        self.layout.addWidget(self.laser_combobox)

        #self.laser_combobox.setSizePolicy(self.sizePolicy)

        self.setLayout(self.layout)

    def launch_nidaq_instance(self):
        if not self.parent.live_window.state_tracker and self.state_tracker:
            parameters = self.parent.left_window.update_parameters
            print("launched with:", parameters, self.view_combobox.currentText(), "and channel", self.laser_combobox.currentText())
            # not yet implemented

    def button_state_change(self):
        if not self.parent.live_window.state_tracker:

            self.state_tracker = not self.state_tracker
            self.parent.toggle_state()

            if self.state_tracker:
                self.section_button.setStyleSheet("background-color: red")
            else:
                self.section_button.setStyleSheet("")
