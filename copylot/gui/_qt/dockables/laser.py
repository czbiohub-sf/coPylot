from qtpy.QtCore import Qt, Slot
from qtpy.QtGui import QFont
from qtpy.QtWidgets import QWidget, QGridLayout, QLabel, QComboBox


class LaserDockWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.parent = parent

    @property
    def parameters(self):
        raise NotImplementedError("laser.parameters not yet implemented")
