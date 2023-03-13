from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QButtonGroup,
    QVBoxLayout,
)
from widgets.helper_functions.indiv_scan_unit import IndividualScanSetting
from widgets.helper_functions.scanlist_unit import ScanTable
from widgets.helper_functions.messagebox import MessageBox
from widgets.helper_functions.laser_selection_box import LaserSelectionBox
from widgets.helper_functions.startstopbox import StartStop


class MultiPatternControl(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.laser_selection_box = LaserSelectionBox(self.parent)
        self.bg_indiv = IndividualScanSetting(self.parent, self)
        self.bg_table = ScanTable(self)
        self.bg_start = StartStop(self)

        self.msgbox = MessageBox('Current Status')

        # Set layout
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setContentsMargins(5, 0, 5, 0)
        self.layout.addWidget(self.laser_selection_box)
        self.layout.addWidget(self.bg_indiv)
        self.layout.addWidget(self.bg_table)
        self.layout.addWidget(self.bg_start)
        self.layout.addWidget(self.msgbox)
        self.setLayout(self.layout)

