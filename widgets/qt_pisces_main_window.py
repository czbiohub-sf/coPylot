import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qt_textbox_and_slider
import qt_custom_decorations
import qt_view_laser_mode


class MainWidgetWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # run the init of QMainWindow

        self.title = "Pisces Parameter Controller"
        self.left = 10
        self.top = 10
        self.width = 800
        self.height = 500
        self.button_state = False

        self.initUI()

        self.show()  # not shown by default

    def initUI(self):  # Window properties are set in the initUI() method

        @pyqtSlot()
        def toggleState():
            self.button_state = not self.button_state
            for i in range(1, timelapse_layout.count()):
                if i != 1:
                    timelapse_layout.itemAt(i).widget().setDisabled(self.button_state)

            for i in range(0, 2 * len(parameter_list)):  # all widgets in left window (+1 due to no final line break)
                if i % 2 == 0:
                    left_window_layout.itemAt(i).widget().setDisabled(self.button_state)

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        #  initialize layout
        window_layout = QHBoxLayout()

        # Left window
        left_window_layout = QVBoxLayout()
        left_window_layout.setAlignment(Qt.AlignTop)

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

        # add instances of qt_textbox_and_slider widget with parameters from list to vertical master layout
        for i in parameter_list:
            left_window_layout.addWidget(qt_textbox_and_slider.InitializeSliderTextB(*i))
            left_window_layout.addWidget(qt_custom_decorations.LineBreak(Qt.AlignTop))

        #  create container for left_window_layout that can be contained by scroll bar widget
        left_widget = QWidget()
        left_widget.setLayout(left_window_layout)

        #  add scroll bar area that contains left window widget
        left_scroll_bar = QScrollArea()
        left_scroll_bar.setMaximumWidth(420)
        left_scroll_bar.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        left_scroll_bar.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left_scroll_bar.setWidgetResizable(False)
        left_scroll_bar.setStyleSheet("background : lightgray;")
        left_scroll_bar.setWidget(left_widget)

        # Right window
        right_window_layout = QVBoxLayout()
        # right_window_layout.setAlignment(Qt.AlignTop)

        #######################################################

        # View control section
        view_layout = QVBoxLayout()
        view_layout.setAlignment(Qt.AlignTop)
        view_button = QPushButton("View")
        view_layout.addWidget(view_button)

        # placeholders for future selection options
        view_combobox_view = QComboBox()
        view_combobox_view.addItem("view 1")
        view_combobox_view.addItem("view 2")
        view_layout.addWidget(view_combobox_view)

        laser_combobox_view = QComboBox()
        laser_combobox_view.addItem("...Hz laser")
        laser_combobox_view.addItem("...Hz laser")
        view_layout.addWidget(laser_combobox_view)

        right_window_layout.addLayout(view_layout)

        #######################################################

        # Timelapse control section
        timelapse_layout = QVBoxLayout()
        timelapse_layout.setAlignment(Qt.AlignTop)

        timelapse_layout.addWidget(qt_custom_decorations.LineBreak(Qt.AlignTop))

        timelapse_button = QPushButton("Timelapse")
        timelapse_layout.addWidget(timelapse_button)

        timelapse_button.pressed.connect(toggleState)

        # placeholders for future selection options
        view_combobox_timelapse = QComboBox()
        view_combobox_timelapse.addItem("view 1")
        view_combobox_timelapse.addItem("view 2")
        timelapse_layout.addWidget(view_combobox_timelapse)

        laser_combobox_timelapse = QComboBox()
        laser_combobox_timelapse.addItem("...Hz laser")
        laser_combobox_timelapse.addItem("...Hz laser")
        timelapse_layout.addWidget(laser_combobox_timelapse)

        right_window_layout.addLayout(timelapse_layout)

        testCount = timelapse_layout.count()
        test_children = timelapse_layout.children()
        test_return = timelapse_layout.itemAt(2).widget()
        print(test_return)
        print(test_children)
        print(testCount)

        # add instances of qt_view_laser_mode widget with custom button name and whether a line break is needed
        # view_window = qt_view_laser_mode.InitializeComboButton(None, "View")
        # laser_window = qt_view_laser_mode.InitializeComboButton(None, "Timelapse", True, True)

        # right_window_layout.addWidget(view_window)
        # right_window_layout.addWidget(laser_window)

        # add left and right window components to main window (left is a widget due to scroll bar)
        window_layout.addWidget(left_scroll_bar)
        window_layout.addLayout(right_window_layout)

        # container for main window layout that can be set as central widget
        main_widget = QWidget()
        main_widget.setLayout(window_layout)

        self.setCentralWidget(main_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWidgetWindow()
    sys.exit(app.exec())
