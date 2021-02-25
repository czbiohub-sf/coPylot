import sys
from functools import reduce
from operator import ior

import qdarkstyle
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QStatusBar, QApplication, QWidget, QDockWidget

from widgets.gui.qt_live_control import LiveControl
from widgets.gui.qt_parameters_widget import ParametersWidget
from widgets.gui.qt_timelapse_control import TimelapseControl


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title = "Pisces Parameter Controller"
        self.left = 10
        self.top = 10
        self.width = 700
        self.height = 500

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setDockOptions(QMainWindow.AnimatedDocks | QMainWindow.AllowNestedDocks)

        # initialize docks
        self.live_dock = QDockWidget("Live", self)
        self.timelapse_dock = QDockWidget("Timelapse", self)
        self.parameters_dock = QDockWidget("Parameters", self)

        # set common configurations for docks
        self.dock_list = [self.live_dock, self.timelapse_dock, self.parameters_dock]
        for dock in self.dock_list:
            self._applyDockConfig(dock)

        # set maximum dock sizes
        self.live_dock.setMaximumSize(200, 140)
        self.timelapse_dock.setMaximumSize(200, 140)
        self.parameters_dock.setMaximumSize(500, 650)

        # initialize widgets and assign to their dock
        self.live_widget = LiveControl(self, "Live Mode")
        self.live_dock.setWidget(self.live_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.live_dock)

        self.timelapse_widget = TimelapseControl(self, "Timelapse Mode")
        self.timelapse_dock.setWidget(self.timelapse_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.timelapse_dock)

        self.parameters_widget = ParametersWidget(self)
        self.parameters_dock.setWidget(self.parameters_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.parameters_dock)

        # split horizontal and vertical space between docks
        self.splitDockWidget(self.parameters_dock, self.live_dock, Qt.Horizontal)
        self.splitDockWidget(self.live_dock, self.timelapse_dock, Qt.Vertical)

        # create status bar that is updated from live and timelapse control classes
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # set placeholder central widget
        self.central_widget = QWidget()
        self.central_widget.hide()
        self.setCentralWidget(self.central_widget)

        self.show()

    def _applyDockConfig(self, dock):
        dock.setFeatures(
                QDockWidget.DockWidgetClosable
                | QDockWidget.DockWidgetMovable
                | QDockWidget.DockWidgetFloatable
            )
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    sys.exit(app.exec())
