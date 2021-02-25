import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qdarkstyle
from widgets.gui import qt_parameters_widget, qt_mode_widget
from widgets.gui.qt_live_control import LiveControl
from widgets.gui.qt_timelapse_control import TimelapseControl


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # run the init of QMainWindow

        self.title = "Pisces Parameter Controller"
        self.left = 10
        self.top = 10
        self.width = 650
        self.height = 700

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.central_widget = QWidget()
        self.central_widget.hide()
        self.setCentralWidget(self.central_widget)

        self.setDockOptions(QMainWindow.AnimatedDocks | QMainWindow.AllowNestedDocks)

        self.live_dock = QDockWidget("Live", self)
        #self.live_dock.setMaximumSize(200, 300)
        self.live_dock.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        #self.mode_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        #self.live_widget = qt_mode_widget.ModeWidget(self)
        self.live_widget = LiveControl(self, "Live Mode")
        self.live_dock.setWidget(self.live_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.live_dock)

        self.timelapse_dock = QDockWidget("Timelapse", self)
        #self.timelapse_dock.setMaximumSize(200, 300)
        self.timelapse_dock.setFeatures(
            QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        # self.mode_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.timelapse_widget = TimelapseControl(self, "Timelapse Mode")
        self.timelapse_dock.setWidget(self.timelapse_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.timelapse_dock)

        self.parameters_dock = QDockWidget("Parameters", self)
        #self.parameters_dock.setMaximumSize(500, 650)
        self.parameters_dock.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        #self.parameters_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.parameters_widget = qt_parameters_widget.ParametersWidget(self)
        self.parameters_dock.setWidget(self.parameters_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.parameters_dock)

        self.splitDockWidget(self.parameters_dock, self.live_dock, Qt.Horizontal)

        self.splitDockWidget(self.live_dock, self.timelapse_dock, Qt.Vertical)

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    sys.exit(app.exec())
