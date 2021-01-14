import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import TextBox_and_Slider
import custom_decorations


class MainWidgetWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # run the init of QMainWindow

        self.title = "Pisces Parameter Controller"
        self.left = 10
        self.top = 10
        self.width = 800
        self.height = 500
        self.initUI()

        self.show()  # not shown by default

    def initUI(self):  # Window properties are set in the initUI() method
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        #  initialize layout
        window_layout = QHBoxLayout()

        right_window_layout = QVBoxLayout()
        right_window_layout.setAlignment(Qt.AlignTop)
        right_window_layout.addWidget(QPushButton("Live Mode"))

        left_window_layout = QVBoxLayout()
        left_window_layout.setAlignment(Qt.AlignTop)

        #  add widgets to vertical master layout
        left_window_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "exposure", 0.001, 1, float, 0.001, 0.02))
        left_window_layout.addWidget(custom_decorations.LineBreak())

        left_window_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "nb_timepoints", 1, 10000, int, 1, 600))
        left_window_layout.addWidget(custom_decorations.LineBreak())

        left_window_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "scan_step", 0.01, 1, float, 0.01, 0.1))
        left_window_layout.addWidget(custom_decorations.LineBreak())

        left_window_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "stage_scan_range", 0, 10000, float, 0.01, 1000))
        left_window_layout.addWidget(custom_decorations.LineBreak())

        left_window_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "vertical_pixels", 0, 4000, int, 1, 2048))
        left_window_layout.addWidget(custom_decorations.LineBreak())

        left_window_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "num_samples", 0, 100, int, 1, 20))
        left_window_layout.addWidget(custom_decorations.LineBreak())

        left_window_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "offset_view1", 0, 3180, float, 0.1, 1550))
        left_window_layout.addWidget(custom_decorations.LineBreak())

        left_window_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "offset_view2", 0, 3180, float, 0.1, 1650))
        left_window_layout.addWidget(custom_decorations.LineBreak())

        left_window_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "view1_galvo1", -10, 10, float, 0.01, 4.2))
        left_window_layout.addWidget(custom_decorations.LineBreak())

        left_window_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "view1_galvo2", -10, 10, float, 0.01, -4.08))
        left_window_layout.addWidget(custom_decorations.LineBreak())

        left_window_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "view2_galvo1", -10, 10, float, 0.01, -4.37))
        left_window_layout.addWidget(custom_decorations.LineBreak())

        left_window_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "view2_galvo2", -10, 10, float, 0.01, 3.66))
        left_window_layout.addWidget(custom_decorations.LineBreak())

        left_window_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "stripe_reduction_range", 0, 10, float, 0.01, 0.1))
        left_window_layout.addWidget(custom_decorations.LineBreak())

        left_window_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "stripe_reduction_offset", -10, 10, float, 0.01, 0.58))
        left_window_layout.addWidget(custom_decorations.LineBreak())

        #  create container for left_window_layout that can be contained by scroll bar widget
        left_widget = QWidget()  # QWidget() acts as a container for the laid out widgets - base class for all widgets
        left_widget.setLayout(left_window_layout)

        #  add scroll bar area that contains left window widget
        left_scroll_bar = QScrollArea()
        left_scroll_bar.setMaximumWidth(self.width / 2)
        left_scroll_bar.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        left_scroll_bar.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        left_scroll_bar.setWidgetResizable(True)
        left_scroll_bar.setStyleSheet("background : lightgray;")
        left_scroll_bar.setWidget(left_widget)

        # add left and right window components to main window (left is a widget due to scroll bar)
        window_layout.addWidget(left_scroll_bar)
        window_layout.addLayout(right_window_layout)

        # container for main window layout that can be set as central widget
        mainWidget = QWidget()
        mainWidget.setLayout(window_layout)

        self.setCentralWidget(mainWidget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWidgetWindow()
    sys.exit(app.exec())
