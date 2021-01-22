import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qt_textbox_and_slider
import qt_custom_decorations


class left_window(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        # column labels
        self.label_layout = QHBoxLayout()
        self.controls_label_layout = QHBoxLayout()

        self.myFont = QFont()
        self.myFont.setBold(True)

        # define spacing such that titles are justified to widgets they describe
        self.label_layout.setContentsMargins(0, 0, 0, 0)
        self.controls_label_layout.setContentsMargins(135, 0, 0, 0)
        self.controls_label_layout.setSpacing(20)

        # create label objects and set bold
        self.parameter_label = QLabel("Parameters")
        self.parameter_label.setFont(self.myFont)
        self.value_label = QLabel("Values")
        self.value_label.setFont(self.myFont)
        self.slider_label = QLabel("Sliders")
        self.slider_label.setFont(self.myFont)

        self.label_layout.addWidget(self.parameter_label)
        self.controls_label_layout.addWidget(self.value_label)
        self.controls_label_layout.addWidget(self.slider_label)

        self.controls_label_layout.setAlignment(Qt.AlignLeft)
        self.label_layout.addLayout(self.controls_label_layout)

        self.layout.addLayout(self.label_layout)
        self.label_layout.addStretch(1)
        self.layout.addWidget(qt_custom_decorations.LineBreak(Qt.AlignTop))

        # parameters

        # add instances of qt_textbox_and_slider widget with parameters from list to vertical master layout
        self.parameter_list = [[self, "exposure", 0.001, 1, float, 0.001, 0.02],
                               [self, "nb_timepoints", 1, 10000, int, 1, 600],
                               [self, "scan_step", 0.01, 1, float, 0.01, 0.1],
                               [self, "stage_scan_range", 0, 10000, float, 0.01, 1000],
                               [self, "vertical_pixels", 0, 4000, int, 1, 2048],
                               [self, "num_samples", 0, 100, int, 1, 20],
                               [self, "offset_view1", 0, 3180, float, 0.1, 1550],
                               [self, "offset_view2", 0, 3180, float, 0.1, 1650],
                               [self, "view1_galvo1", -10, 10, float, 0.01, 4.2],
                               [self, "view1_galvo2", -10, 10, float, 0.01, -4.08],
                               [self, "view2_galvo1", -10, 10, float, 0.01, -4.37],
                               [self, "view2_galvo2", -10, 10, float, 0.01, 3.66],
                               [self, "stripe_reduction_range", 0, 10, float, 0.01, 0.1],
                               [self, "stripe_reduction_offset", -10, 10, float, 0.01, 0.58]]

        for i in self.parameter_list:
            self.layout.addWidget(qt_textbox_and_slider.InitializeSliderTextB(*i))
            self.layout.addWidget(qt_custom_decorations.LineBreak(Qt.AlignTop))

        self.setLayout(self.layout)
