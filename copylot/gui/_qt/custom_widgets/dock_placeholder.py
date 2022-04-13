from qtpy.QtWidgets import QWidget, QHBoxLayout, QPushButton


class DockPlaceholder(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.parent = parent

        self.placeholder_layout = QHBoxLayout()
        self.placeholder_layout.setContentsMargins(0, 0, 0, 0)

        self.load_button = QPushButton("Load")
        self.placeholder_layout.addWidget(self.load_button, 0)

        self.setLayout(self.placeholder_layout)
