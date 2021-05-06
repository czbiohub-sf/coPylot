import json
import os.path
import sys
import qdarkstyle
from pathlib import Path
from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QApplication,
    QWidget,
    QDockWidget,
)

from copylot.gui.qt_live_control import LiveControl
from copylot.gui.qt_parameters_widget import ParametersWidget
from copylot.gui.qt_timelapse_control import TimelapseControl
from copylot.gui.qt_water_dispenser_widget import WaterDispenser


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.threadpool = QThreadPool()

        self.title = "Pisces Parameter Controller"
        self.left = 10
        self.top = 10
        self.width = 900
        self.height = 1000

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setDockOptions(QMainWindow.AnimatedDocks | QMainWindow.AllowNestedDocks)

        self.init_defaults = [
            ["exposure", 0.001, 1, 0.02],
            ["nb_timepoints", 1, 10000, 600],
            ["scan_step", 0.01, 1, 0.1],
            ["stage_scan_range", 0, 10000, 1000],
            ["vertical_pixels", 0, 4000, 2048],
            ["num_samples", 0, 100, 20],
            ["offset_view1", 0, 3180, 1550],
            ["offset_view2", 0, 3180, 1650],
            ["view1_galvo1", -10, 10, 4.2],
            ["view1_galvo2", -10, 10, -4.08],
            ["view2_galvo1", -10, 10, -4.37],
            ["view2_galvo2", -10, 10, 3.66],
            ["stripe_reduction_range", 0, 10, 0.1],
            ["stripe_reduction_offset", -10, 10, 0.58],
        ]

        try:
            with open(
                os.path.join(str(Path.home()), "coPylot_parameters.txt"), "r"
            ) as json_file:
                self.defaults = json.load(json_file)

        except FileNotFoundError:  # construct initial defaults.txt fileself.defaults = [3, 6, 25, 100]
            self.defaults = {
                "parameters": {},
                "live": {"view": 0, "laser": 0},
                "timelapse": {"view": 0, "laser": 0},
                "water": {
                    "interval": 3,
                    "duration": 6,
                    "freq": 25,
                    "amp": 100,
                    "serial port": 0,
                    "baudrate": 0,
                },
            }
            for i in range(0, len(self.init_defaults)):
                obj = self.init_defaults[i]
                self.defaults["parameters"][obj[0]] = [obj[3], obj[1], obj[2]]

            with open(
                os.path.join(str(Path.home()), "coPylot_parameters.txt"), "w"
            ) as outfile:
                json.dump(self.defaults, outfile)

        # initialize docks
        self.live_dock = QDockWidget("Live", self)
        self.timelapse_dock = QDockWidget("Timelapse", self)
        self.water_dock = QDockWidget("Water", self)
        self.parameters_dock = QDockWidget("Parameters", self)

        # set common configurations for docks
        self.dock_list = [
            self.live_dock,
            self.timelapse_dock,
            self.water_dock,
            self.parameters_dock,
        ]
        for dock in self.dock_list:
            _apply_dock_config(dock)

        # set maximum dock sizes
        self.live_dock.setFixedSize(200, 150)
        self.timelapse_dock.setFixedSize(200, 170)
        self.water_dock.setFixedSize(200, 260)
        self.parameters_dock.setFixedSize(650, 650)

        # initialize widgets and assign to their dock
        self.live_widget = LiveControl(self, self.threadpool)
        self.live_dock.setWidget(self.live_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.live_dock)

        self.timelapse_widget = TimelapseControl(self, self.threadpool)
        self.timelapse_dock.setWidget(self.timelapse_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.timelapse_dock)

        self.water_widget = WaterDispenser(self, self.threadpool)
        self.water_dock.setWidget(self.water_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.water_dock)

        self.parameters_widget = ParametersWidget(self)
        self.parameters_dock.setWidget(self.parameters_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.parameters_dock)

        # split horizontal and vertical space between docks
        self.splitDockWidget(self.parameters_dock, self.live_dock, Qt.Horizontal)
        self.splitDockWidget(self.live_dock, self.timelapse_dock, Qt.Vertical)
        self.splitDockWidget(self.timelapse_dock, self.water_dock, Qt.Vertical)

        # create status bar that is updated from live and timelapse control classes
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # set placeholder central widget
        self.central_widget = QWidget()
        self.central_widget.hide()
        self.setCentralWidget(self.central_widget)

        self.show()


def _apply_dock_config(dock):
    dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
    dock.setAllowedAreas(
        Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea
    )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    sys.exit(app.exec())
