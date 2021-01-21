import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qdarkstyle
import qt_textbox_and_slider
import qt_custom_decorations
import qt_view_laser_mode


class MainWidgetWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # run the init of QMainWindow

        self.title = "Pisces Parameter Controller"
        self.left = 10
        self.top = 10
        self.width = 650
        self.height = 500
        self.button_state = True

        # initialize layouts
        self.window_layout = QHBoxLayout()
        self.left_window_layout = QVBoxLayout()
        self.right_window_layout = QVBoxLayout()
        self.label_layout = QHBoxLayout()
        self.controls_label_layout = QHBoxLayout()

        # initialize right window widgets
        self.view_window = qt_view_laser_mode.InitializeComboButton(self, "View")
        self.timelapse_window = qt_view_laser_mode.InitializeComboButton(self, "Timelapse", True, True)

        self.initUI()
        self.toggleState()

        self.show()  # not shown by default

    def initUI(self):  # Window properties are set in the initUI() method

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Left window
        self.left_window_layout.setAlignment(Qt.AlignTop)

        # column labels
        myFont = QFont()
        myFont.setBold(True)

        # define spacing such that titles are justified to widgets they describe
        self.label_layout.setContentsMargins(0, 0, 0, 0)
        self.controls_label_layout.setContentsMargins(135, 0, 0, 0)
        self.controls_label_layout.setSpacing(22)

        # create label objects and set bold
        parameter_label = QLabel("Parameters")
        parameter_label.setFont(myFont)
        value_label = QLabel("Values")
        value_label.setFont(myFont)
        slider_label = QLabel("Sliders")
        slider_label.setFont(myFont)

        self.label_layout.addWidget(parameter_label)
        self.controls_label_layout.addWidget(value_label)
        self.controls_label_layout.addWidget(slider_label)

        self.controls_label_layout.setAlignment(Qt.AlignLeft)
        self.label_layout.addLayout(self.controls_label_layout)

        self.left_window_layout.addLayout(self.label_layout)
        self.label_layout.addStretch(1)
        self.left_window_layout.addWidget(qt_custom_decorations.LineBreak(Qt.AlignTop))

        # add instances of qt_textbox_and_slider widget with parameters from list to vertical master layout
        parameter_list = [[None, "exposure", 0.001, 1, float, 0.001, 0.02],
                          [None, "nb_timepoints", 1, 10000, int, 1, 600],
                          [None, "scan_step", 0.01, 1, float, 0.01, 0.1],
                          [None, "stage_scan_range", 0, 10000, float, 0.01, 1000],
                          [None, "vertical_pixels", 0, 4000, int, 1, 2048],
                          [None, "num_samples", 0, 100, int, 1, 20],
                          [None, "offset_view1", 0, 3180, float, 0.1, 1550],
                          [None, "offset_view2", 0, 3180, float, 0.1, 1650],
                          [None, "view1_galvo1", -10, 10, float, 0.01, 4.2],
                          [None, "view1_galvo2", -10, 10, float, 0.01, -4.08],
                          [None, "view2_galvo1", -10, 10, float, 0.01, -4.37],
                          [None, "view2_galvo2", -10, 10, float, 0.01, 3.66],
                          [None, "stripe_reduction_range", 0, 10, float, 0.01, 0.1],
                          [None, "stripe_reduction_offset", -10, 10, float, 0.01, 0.58]]

        for i in parameter_list:
            self.left_window_layout.addWidget(qt_textbox_and_slider.InitializeSliderTextB(*i))
            self.left_window_layout.addWidget(qt_custom_decorations.LineBreak(Qt.AlignTop))

        # Right window
        self.right_window_layout.addWidget(self.view_window)
        self.right_window_layout.addWidget(self.timelapse_window)

        # add left and right window components to main window
        left_widget = QWidget()
        left_widget.setFixedWidth(500)
        left_widget.setLayout(self.left_window_layout)

        self.window_layout.addWidget(left_widget)
        self.window_layout.addLayout(self.right_window_layout)

        # container for main window layout that can be set as central widget
        main_widget = QWidget()
        main_widget.setLayout(self.window_layout)

        self.setCentralWidget(main_widget)

    @pyqtSlot()
    def toggleState(self):
        """
        slot decorated function to disable all input widgets when button to enter timelapse mode is pressed
        """
        self.button_state = not self.button_state
        for j in range(1, self.timelapse_window.layout().count()):
            if j != 1:
                self.timelapse_window.layout().itemAt(j).widget().setDisabled(self.button_state)

        for k in range(0, 29):
            if k % 2 == 0 and k != 0:
                self.left_window_layout.itemAt(k).widget().setDisabled(self.button_state)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWidgetWindow()
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    sys.exit(app.exec())
