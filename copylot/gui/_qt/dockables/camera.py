from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
)


class CameraDockWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.parent = parent

        self.main_layout = QHBoxLayout()

        self.parameters_layout = QGridLayout()
        row_index = 0
        parameter_label = QLabel("Exposure duration:", self)
        parameter_editbox = QLineEdit(str(0.01), self)

        self.parameters_layout.addWidget(
            parameter_label, row_index, 0, alignment=Qt.AlignTop
        )
        self.parameters_layout.addWidget(
            parameter_editbox, row_index, 1, alignment=Qt.AlignTop
        )

        self.main_layout.addLayout(self.parameters_layout)

        self.setLayout(self.main_layout)

    @property
    def parameters(self):
        raise NotImplementedError("camera.parameters not yet implemented")
