import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qdarkstyle
from widgets.gui import qt_parameters_widget, qt_mode_widget


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

        self.mode_dock = QDockWidget("Mode Control", self)
        self.mode_dock.setMaximumSize(200, 300)
        self.mode_dock.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.mode_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.mode_widget = qt_mode_widget.ModeWidget(self)
        self.mode_dock.setWidget(self.mode_widget)

        self.addDockWidget(Qt.RightDockWidgetArea, self.mode_dock)

        self.parameters_dock = QDockWidget("Parameters", self)
        self.parameters_dock.setMaximumSize(500, 650)
        self.parameters_dock.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.parameters_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.parameters_widget = qt_parameters_widget.ParametersWidget(self)
        self.parameters_dock.setWidget(self.parameters_widget)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.parameters_dock)

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    sys.exit(app.exec())
