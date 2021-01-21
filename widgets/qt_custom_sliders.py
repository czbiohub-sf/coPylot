import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class DoubleClickableSlider(QSlider):
    def __init__(self, parent):
        super(QSlider, self).__init__(Qt.Horizontal, parent)

        self.parent = parent

    def mouseDoubleClickEvent(self, event):
        self.parent.toggle_range_widgets()


