import json
import os.path
import sys
import qdarkstyle
from pathlib import Path
from qtpy.QtCore import Qt, QThreadPool
from qtpy.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QApplication,
    QDockWidget,
    QLabel,
    QAction,
)

from copylot.gui._qt.custom_widgets.dock_placeholder import DockPlaceholder
from copylot import __version__, logger


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.threadpool = QThreadPool()

        self.title = "Pisces Parameter Controller"
        self.version = __version__

        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        height, width = self.screenRect.height(), self.screenRect.width()

        self.width = width // 3
        self.height = height // 2
        self.left = (width - self.width) // 2
        self.top = (height - self.height) // 2

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
                os.path.join(str(Path.home()), ".coPylot", "coPylot_parameters.txt"),
                "r",
            ) as json_file:
                self.defaults = json.load(json_file)

        except (
            FileNotFoundError
        ):  # construct initial defaults.txt fileself.defaults = [3, 6, 25, 100]
            if not os.path.isdir(os.path.join(str(Path.home()), ".coPylot")):
                os.mkdir(os.path.join(str(Path.home()), ".coPylot"))

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
                os.path.join(str(Path.home()), ".coPylot", "coPylot_parameters.txt"),
                "w",
            ) as outfile:
                json.dump(self.defaults, outfile)

        # set common configurations for docks
        self.dock_list = []

        # initialize docks
        self.dock_widgets_to_initialize = [
            ("live_control", [self, self.threadpool]),
            ("timelapse_control", [self, self.threadpool]),
            ("water_dispenser", [self, self.threadpool]),
            ("laser", [self]),
            ("parameters", [self]),
        ]

        for name, args in self.dock_widgets_to_initialize:
            dock_widget = QDockWidget(self)
            dock_widget.setTitleBarWidget(QLabel(name))
            self.dock_list.append(dock_widget)

        for dock in self.dock_list:
            _apply_dock_config(dock)

        # initialize widgets and assign to their dock
        for idx, (name, args) in enumerate(self.dock_widgets_to_initialize):
            self.dock_list[idx].setWidget(
                DockPlaceholder(self, self.dock_list[idx], name, args)
            )

        for idx, dock in enumerate(self.dock_list):
            if idx == 0:
                self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_list[idx])
            else:
                self.splitDockWidget(
                    self.dock_list[idx - 1], self.dock_list[idx], Qt.Vertical
                )

        # create status bar that is updated from live and timelapse control classes
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Menu bar
        self.setupMenubar()

    def closeEvent(self, event):
        logger.info("closeEvent of mainwindow is called")
        app = QApplication.instance()
        app.quit()

    def setupMenubar(self):
        """Method to populate menubar."""
        mainMenu = self.menuBar()
        mainMenu.setNativeMenuBar(False)

        helpMenu = mainMenu.addMenu(' &Help')

        # Help Menu
        versionButton = QAction("ver" + self.version, self)
        helpMenu.addAction(versionButton)


def _apply_dock_config(dock):
    dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
    dock.setAllowedAreas(
        Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea
    )


def run():
    """Method to run GUI

    Parameters
    ----------
    ver : str
        string of aydin version number

    """
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    run()
