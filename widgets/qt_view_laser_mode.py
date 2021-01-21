import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qt_custom_decorations


class InitializeComboButton(QWidget):
    def __init__(self, parent, button_name, add_line_break=False, can_disable=False):
        super(QWidget, self).__init__(parent)

        self.parent = parent
        self.button_name = button_name
        self.add_line_break = add_line_break
        self.can_disable = can_disable

        if self.can_disable:
            self.button_state = False

        self.initUI()

    def initUI(self):

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        if self.add_line_break:
            layout.addWidget(qt_custom_decorations.LineBreak(Qt.AlignTop))

        # add labeled button that, if can_disable = True, disables the comboboxes, preventing input change
        section_button = QPushButton(self.button_name)
        if self.can_disable:
            section_button.pressed.connect(self.parent.toggleState)

        layout.addWidget(section_button)

        # placeholders for future selection options
        view_combobox = QComboBox()
        view_combobox.addItem("view 1")
        view_combobox.addItem("view 2")
        layout.addWidget(view_combobox)

        laser_combobox = QComboBox()
        laser_combobox.addItem("...Hz laser")
        laser_combobox.addItem("...Hz laser")
        layout.addWidget(laser_combobox)

        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    testWidget = InitializeComboButton("test")
    sys.exit(app.exec())
