import importlib

from qtpy.QtWidgets import QWidget, QHBoxLayout, QPushButton

from copylot.gui._qt import dockables


class DockPlaceholder(QWidget):
    def __init__(self, parent, dock, widget_to_load, widget_name, *args, **kwargs):
        super().__init__(*args, **kwargs)

        get_widget_instance_from_name(parent, widget_name)

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


def get_widget_instance_from_name(parent, name: str):
    response = importlib.import_module(dockables.__name__ + '.' + name)
    print(response)
    print(dir(response))
    # elem = [
    #     x
    #     for x in dir(response)
    #     if (name.replace("_", "") + "Regressor").lower() in x.lower()
    # ][
    #     0
    # ]  # class name

    # elem_class = response.__getattribute__(elem)
    #
    # return elem_class(parent)
