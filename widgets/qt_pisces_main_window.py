import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qdarkstyle
import qt_textbox_and_slider
import qt_custom_decorations
import qt_view_laser_mode
import qt_left_window


class MainWidgetWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # run the init of QMainWindow

        self.title = "Pisces Parameter Controller"
        self.left = 10
        self.top = 10
        self.width = 650
        self.height = 500

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.button_state = False

        # initialize layouts
        self.window_layout = QHBoxLayout()
        self.right_window_layout = QVBoxLayout()

        # Right window
        self.view_window = qt_view_laser_mode.InitializeComboButton(self, "View")
        self.timelapse_window = qt_view_laser_mode.InitializeComboButton(self, "Timelapse", True, True)

        self.right_window_layout.addWidget(self.view_window)
        self.right_window_layout.addWidget(self.timelapse_window)

        self.window_layout.addWidget(qt_left_window.left_window(self))  # left window
        self.window_layout.addLayout(self.right_window_layout)

        # container for main window layout that can be set as central widget
        self.main_widget = QWidget()
        self.main_widget.setLayout(self.window_layout)

        self.setCentralWidget(self.main_widget)

        self.show()  # not shown by default

    @pyqtSlot()
    def toggleState(self):
        """
        slot decorated function to disable all input widgets when button to enter timelapse mode is pressed
        """
        self.button_state = not self.button_state
        for j in range(1, self.timelapse_window.layout.count()):
            if j != 1:
                self.timelapse_window.layout.itemAt(j).widget().setDisabled(self.button_state)

        self.window_layout.itemAt(0).widget().setDisabled(self.button_state)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWidgetWindow()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    sys.exit(app.exec())
