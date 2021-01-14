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
        self.width = 400
        self.height = 500
        self.initUI()

        self.show()  # not shown by default

    def initUI(self):  # Window properties are set in the initUI() method
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        #  initialize layout
        master_layout = QVBoxLayout()
        master_layout.setAlignment(Qt.AlignTop)

        #  add widgets to vertical master layout
        master_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "exposure", 0.001, 1, float, 0.001, 0.02))
        master_layout.addWidget(custom_decorations.LineBreak())
        master_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "nb_timepoints", 1, 10000, int, 1, 600))
        master_layout.addWidget(custom_decorations.LineBreak())
        master_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "scan_step", 0.01, 1, float, 0.01, 0.1))
        master_layout.addWidget(custom_decorations.LineBreak())
        master_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "stage_scan_range", 0, 10000, float, 0.01, 1000))
        master_layout.addWidget(custom_decorations.LineBreak())
        master_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "vertical_pixels", 0, 4000, int, 1, 2048))
        master_layout.addWidget(custom_decorations.LineBreak())
        master_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "num_samples", 0, 100, int, 1, 20))
        master_layout.addWidget(custom_decorations.LineBreak())
        master_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "offset_view1", 0, 3180, float, 0.1, 1550))
        master_layout.addWidget(custom_decorations.LineBreak())
        master_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "offset_view2", 0, 3180, float, 0.1, 1650))
        master_layout.addWidget(custom_decorations.LineBreak())
        master_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "view1_galvo1", -10, 10, float, 0.01, 4.2))
        master_layout.addWidget(custom_decorations.LineBreak())
        master_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "view1_galvo2", -10, 10, float, 0.01, -4.08))
        master_layout.addWidget(custom_decorations.LineBreak())
        master_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "view2_galvo1", -10, 10, float, 0.01, -4.37))
        master_layout.addWidget(custom_decorations.LineBreak())
        master_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "view2_galvo2", -10, 10, float, 0.01, 3.66))
        master_layout.addWidget(custom_decorations.LineBreak())
        master_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "stripe_reduction_range", 0, 10, float, 0.01, 0.1))
        master_layout.addWidget(custom_decorations.LineBreak())
        master_layout.addWidget(TextBox_and_Slider.InitializeSliderTextB(None, "stripe_reduction_offset", -10, 10, float, 0.01, 0.58))
        master_layout.addWidget(custom_decorations.LineBreak())

        #  create base class container for layout and align it centrally
        widget = QWidget()  # QWidget() acts as a container for the laid out widgets - base class for all widgets
        widget.setLayout(master_layout)

        #  add scroll bar
        scroll_bar = QScrollArea()
        scroll_bar.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_bar.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_bar.setWidgetResizable(False)
        scroll_bar.setStyleSheet("background : lightgray;")
        scroll_bar.setWidget(widget)

        self.setCentralWidget(scroll_bar)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWidgetWindow()
    sys.exit(app.exec())
