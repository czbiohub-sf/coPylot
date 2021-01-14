import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class LineBreak(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initUI()

    def initUI(self):
        line_break_layout = QHBoxLayout()

        hline_break = QFrame()
        hline_break.setFrameShape(QFrame.HLine)
        hline_break.setFrameShadow(QFrame.Sunken)
        line_break_layout.setAlignment(Qt.AlignTop)

        line_break_layout.addWidget(hline_break, 0)
        self.setLayout(line_break_layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    line_break = LineBreak()
    sys.exit(app.exec())
