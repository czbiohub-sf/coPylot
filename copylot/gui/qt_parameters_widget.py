import json
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton

from copylot.gui.qt_line_break import LineBreak
from copylot.gui.qt_textbox_and_slider import TextboxAndSlider


class ParametersWidget(QWidget):
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
        self.parameter_list = [
            [self, "exposure", 0.001, 1, float, 0.001, 0.02],
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
            [self, "stripe_reduction_offset", -10, 10, float, 0.01, 0.58],
        ]

        try:
            with open("defaults.txt") as json_file:
                self.defaults = json.load(json_file)

        except FileNotFoundError:
            self.defaults = {"parameters": {}}
            for i in range(
                0, len(self.parameter_list)
            ):  # create defaults.txt file on first launch
                obj = self.parameter_list[i]
                self.defaults["parameters"][obj[1]] = [obj[6], obj[2], obj[3]]

            with open("defaults.txt", "w") as outfile:
                json.dump(self.defaults, outfile)

        self.row_counter = 1
        self.parameter_objects = []

        for i in self.parameter_list:
            textbox_and_slider = TextboxAndSlider(*i, self.row_counter, self.defaults)
            self.parameter_objects.append(textbox_and_slider)
            self.grid_layout.addWidget(
                LineBreak(Qt.AlignTop), self.row_counter + 1, 0, 1, 5
            )

            self.row_counter += 2

        # addition of button to toggle visibility of parameter range input boxes
        self.toggle_button = QPushButton("set range")
        for obj in self.parameter_objects:
            self.toggle_button.pressed.connect(obj.toggle_range_widgets)

        self.grid_layout.addWidget(self.toggle_button, self.row_counter, 0, 1, 4)

        self.defaults_button = QPushButton("set as defaults")
        self.defaults_button.pressed.connect(self.save_defaults)
        self.grid_layout.addWidget(self.defaults_button, self.row_counter, 4, 1, 1)

    @property
    def parameters(self):
        parameter_vals = {}
        for i in range(0, len(self.parameter_objects)):
            parameter_vals[
                self.parameter_objects[i].label.text()
            ] = self.parameter_objects[i].spinbox.value()

        return parameter_vals

    @pyqtSlot()
    def save_defaults(self):
        defaults = {"parameters": {}}
        for i in range(0, len(self.parameter_objects)):
            obj = self.parameter_objects[i]
            defaults["parameters"][obj.label.text()] = [obj.spinbox.value(), *obj.range]

        with open("defaults.txt", "w") as outfile:
            json.dump(defaults, outfile)
