from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qt_textbox_and_slider
import qt_line_break


class LeftWindow(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.parent = parent

        self.grid_layout = QGridLayout()
        self.setLayout(self.grid_layout)
        self.grid_layout.setAlignment(Qt.AlignTop)

        self.my_font = QFont()
        self.my_font.setBold(True)

        # create label objects and set bold
        self.parameter_label = QLabel("Parameters")
        self.parameter_label.setFont(self.my_font)
        self.value_label = QLabel("Values")
        self.value_label.setFont(self.my_font)
        self.slider_label = QLabel("Sliders")
        self.slider_label.setFont(self.my_font)

        self.grid_layout.addWidget(self.parameter_label, 0, 0)
        self.grid_layout.addWidget(self.value_label, 0, 1)
        self.grid_layout.addWidget(self.slider_label, 0, 3)
        self.slider_label.setAlignment(Qt.AlignHCenter)

        # parameters
        # add instances of qt_textbox_and_slider widget with parameters from list to vertical layout
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

        self.row_counter = 1
        self.parameter_objects = []

        for i in self.parameter_list:
            textbox_and_slider = qt_textbox_and_slider.TextboxAndSlider(*i, self.row_counter)
            self.parameter_objects.append(textbox_and_slider)
            self.grid_layout.addWidget(qt_line_break.LineBreak(Qt.AlignTop), self.row_counter + 1, 0, 1, 5)

            self.row_counter += 2
            
        # addition of button to toggle visibility of parameter range input boxes
        self.toggle_button = QPushButton("set range")
        for obj in self.parameter_objects:
            self.toggle_button.pressed.connect(obj.toggle_range_widgets)

        self.grid_layout.addWidget(self.toggle_button, self.row_counter, 0, 1, 5)

    @property
    def update_parameters(self):
        parameter_vals = {}
        for i in range(0, len(self.parameter_objects)):
            parameter_vals[self.parameter_objects[i].label.text()] = self.parameter_objects[i].spinbox.value()

        return parameter_vals
