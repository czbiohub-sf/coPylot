from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from widgets.hardware.control import NIDaq


class LiveControl(QWidget):
    def __init__(self, parent, button_name):
        super(QWidget, self).__init__(parent)

        self.parent = parent
        self.button_name = button_name

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        # add instance launching button
        self.section_button = QPushButton(self.button_name)
        self.section_button.pressed.connect(self.launch_nidaq_instance)
        self.layout.addWidget(self.section_button)

        # placeholders for future selection options
        self.view_combobox = QComboBox()
        self.view_combobox.addItem("view 1")
        self.view_combobox.addItem("view 2")
        self.layout.addWidget(self.view_combobox)
        self.view_combobox.activated.connect(self.launch_nidaq_instance)

        self.laser_combobox = QComboBox()
        self.laser_combobox.addItem("488")
        self.laser_combobox.addItem("561")
        self.layout.addWidget(self.laser_combobox)
        self.laser_combobox.activated.connect(self.launch_nidaq_instance)

        self.setLayout(self.layout)

    def launch_nidaq_instance(self):
        parameters = self.parent.left_window.update_parameters
        print("launched with: ", parameters)
        daq_card = NIDaq(exposure=parameters[0],
                         nb_timepoints=parameters[1],
                         scan_step=parameters[2],
                         stage_scan_range=parameters[3],
                         vertical_pixels=parameters[4],
                         num_samples=parameters[5],
                         offset_view1=parameters[6],
                         offset_view2=parameters[7],
                         view1_galvo1=parameters[8],
                         view1_galvo2=parameters[9],
                         view2_galvo1=parameters[10],
                         view2_galvo2=parameters[11],
                         stripe_reduction_range=parameters[12],
                         stripe_reduction_offset=parameters[13])

        daq_card.select_view(int(self.view_combobox.currentText()[5]))
        daq_card.select_channel_remove_stripes(int(self.laser_combobox.currentText()))
