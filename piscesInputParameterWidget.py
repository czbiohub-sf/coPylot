import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import exposure_widget
import nb_timepoints_widget


class MainWidgetWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # run the init of QMainWindow

        self.title = "Pisces Parameter Controller"
        self.left = 10
        self.top = 10
        self.width = 300
        self.height = 200
        self.initUI()

    def initUI(self):  # Window properties are set in the initUI() method
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        #  initialize layout
        master_layout = QVBoxLayout()
        master_layout.setAlignment(Qt.AlignTop)

        # create a line break widget
        line_break_layout3 = QHBoxLayout()
        hline_break = QFrame()
        hline_break.setFrameShape(QFrame.HLine)
        hline_break.setFrameShadow(QFrame.Sunken)
        line_break_layout3.addWidget(hline_break, 0)
        line_break_layout3.setAlignment(Qt.AlignTop)

        #  add widgets to vertical master layout
        master_layout.addWidget(exposure_widget.DefineExposureWidget(self))  # exposure selection widget
        master_layout.addLayout(line_break_layout3)
        master_layout.addWidget(nb_timepoints_widget.DefineNumberTimepointsWidget(self))  # nb_timepoints widget

        #  create base class container for layout and align it centrally
        widget = QWidget()  # QWidget() acts as a container for the laid out widgets - base class for all widgets
        widget.setLayout(master_layout)

        self.setCentralWidget(widget)

        self.show()  # not shown by default


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWidgetWindow()
    sys.exit(app.exec())
