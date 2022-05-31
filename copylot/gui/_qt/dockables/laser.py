from qtpy.QtWidgets import QWidget, QHBoxLayout, QPushButton

from copylot.gui._qt.custom_widgets.line_break import QVLineBreakWidget


class LaserDockWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.parent = parent

        self.main_layout = QHBoxLayout()
        self.power_button = QPushButton("Power")
        self.power_button.clicked.connect(self.power_button.toggle)
        self.main_layout.addWidget(self.power_button)

        self.main_layout.addWidget(QVLineBreakWidget(self))

        self.setLayout(self.main_layout)

    @property
    def parameters(self):
        raise NotImplementedError("laser.parameters not yet implemented")
