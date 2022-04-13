from qtpy.QtWidgets import QWidget, QHBoxLayout, QPushButton


class DockPlaceholder(QWidget):
    def __init__(self, parent, dock, widget_to_load, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.parent = parent
        self.dock = dock
        self.widget_to_load = widget_to_load

        self.placeholder_layout = QHBoxLayout()
        self.placeholder_layout.setContentsMargins(0, 0, 0, 0)

        self.load_button = QPushButton("Load")
        self.load_button.clicked.connect(self.load_widget)
        self.placeholder_layout.addWidget(self.load_button, 0)

        self.setLayout(self.placeholder_layout)

    def load_widget(self):
        self.dock.setWidget(self.widget_to_load)
        self.parent.restoreDockWidget(self.dock)
