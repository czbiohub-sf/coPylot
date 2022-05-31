from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QHBoxLayout, QFrame


class QHLineBreakWidget(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.horizontal_line_break = QFrame()
        self.horizontal_line_break.setFrameShape(QFrame.HLine)
        self.horizontal_line_break.setFrameShadow(QFrame.Sunken)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.addWidget(self.horizontal_line_break, 0)

        self.setLayout(self.main_layout)


class QVLineBreakWidget(QWidget):
    def __init__(self, parent):
        super(QVLineBreakWidget, self).__init__(parent)
        self.parent = parent

        self.main_layout = QHBoxLayout()
        self.vertical_line_break = QFrame()
        self.vertical_line_break.setFrameShape(QFrame.VLine)
        self.vertical_line_break.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(self.vertical_line_break)
        self.main_layout.setAlignment(Qt.AlignLeft)
        self.setLayout(self.main_layout)
