from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QHBoxLayout, QPushButton, QGridLayout, QLabel, QLineEdit, QSlider

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

        self.parameters_layout = QGridLayout()
        row_index = 0
        parameter_label = QLabel("Laser Power:", self)
        parameter_editbox = QLineEdit(str(0.01), self)
        parameter_slider = QSlider(Qt.Horizontal)

        self.parameters_layout.addWidget(
            parameter_label, row_index, 0, alignment=Qt.AlignTop
        )
        self.parameters_layout.addWidget(
            parameter_editbox, row_index, 1, alignment=Qt.AlignTop
        )
        self.parameters_layout.addWidget(
            parameter_slider, row_index, 2, alignment=Qt.AlignTop
        )

        self.main_layout.addLayout(self.parameters_layout)

        self.setLayout(self.main_layout)

    @property
    def parameters(self):
        raise NotImplementedError("laser.parameters not yet implemented")
