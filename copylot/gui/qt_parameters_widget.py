import json
import threading
import time
import os
from datetime import datetime
from pathlib import Path
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton, QComboBox

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
            [self, "exposure", float, 0.001],
            [self, "nb_timepoints", int, 1],
            [self, "scan_step", float, 0.01],
            [self, "stage_scan_range", float, 0.01],
            [self, "vertical_pixels", int, 1],
            [self, "num_samples", int, 1],
            [self, "offset_view1", float, 0.1],
            [self, "offset_view2", float, 0.1],
            [self, "view1_galvo1", float, 0.01],
            [self, "view1_galvo2", float, 0.01],
            [self, "view2_galvo1", float, 0.01],
            [self, "view2_galvo2", float, 0.01],
            [self, "stripe_reduction_range", float, 0.01],
            [self, "stripe_reduction_offset", float, 0.01],
        ]

        self.row_counter = 1
        self.parameter_objects = []

        for i in self.parameter_list:
            textbox_and_slider = TextboxAndSlider(
                *i, self.row_counter, self.parent.defaults
            )
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
    def save_defaults(self, log=False):
        for i in range(0, len(self.parameter_objects)):
            obj = self.parameter_objects[i]
            self.parent.defaults["parameters"][obj.label.text()] = [
                obj.spinbox.value(),
                *obj.range,
            ]

        self.parent.defaults["timelapse"][
            "view"
        ] = self.parent.timelapse_widget.view_combobox.currentIndex()
        self.parent.defaults["timelapse"][
            "laser"
        ] = self.parent.timelapse_widget.laser_combobox.currentIndex()

        self.parent.defaults["live"][
            "view"
        ] = self.parent.live_widget.view_combobox.currentIndex()
        self.parent.defaults["live"][
            "laser"
        ] = self.parent.live_widget.laser_combobox.currentIndex()

        param_counter = 0
        for param in self.parent.water_widget.param_list:
            self.parent.defaults["water"][
                self.parent.water_widget.param_names[param_counter]
            ] = (param.currentIndex() if type(param) == QComboBox else param.value())
            param_counter += 1

        if not log:
            with open(
                os.path.join(str(Path.home()), "coPylot_parameters.txt"), "w"
            ) as outfile:
                json.dump(self.parent.defaults, outfile)
        else:
            with open(
                os.path.join(
                    str(Path.home()),
                    "log-" + datetime.now().strftime("%d-%m-%Y:%H:%M:%S") + ".txt",
                ),
                "w",
            ) as outfile:
                json.dump(self.parent.defaults, outfile)

        def status():
            current_msg = self.parent.status_bar.currentMessage()
            self.parent.status_bar.showMessage("defaults saved!")
            time.sleep(0.7)
            if self.parent.status_bar.currentMessage() == "defaults saved!":
                self.parent.status_bar.showMessage(current_msg)

        threading.Thread(target=status, args=[]).start()
