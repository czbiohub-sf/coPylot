from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QLabel,
    QButtonGroup,
    QRadioButton,
    QGroupBox,
    QGridLayout,
    QSizePolicy,
)


class LaserSelectionBox(QGroupBox):
    def __init__(self, tabmanager):
        super().__init__()
        self.tabmanager = tabmanager
        self.setTitle('Select laser')
        # Create buttons
        self.laser1_select = QRadioButton('405nm Laser')
        self.laser2_select = QRadioButton('785nm Laser')
        self.laser_selection = QButtonGroup(self)
        self.laser_selection.addButton(self.laser1_select, 0)
        self.laser_selection.addButton(self.laser2_select, 1)
        self.laser_selection.buttons()[self.tabmanager.parent.current_laser].setChecked(True)
        # Create status labels
        self.laser1_status = QLabel('Not calibrated')
        self.laser1_status.setStyleSheet('color: gray')
        self.laser2_status = QLabel('Not calibrated')
        self.laser2_status.setStyleSheet('color: gray')
        # set layout
        self.setStyleSheet('QGroupBox::title {font-size: 14pt;}')
        self.laser_box_grid = QGridLayout()
        self.laser_box_grid.addWidget(self.laser1_select, 0, 0)
        self.laser_box_grid.addWidget(self.laser2_select, 1, 0)
        self.laser_box_grid.addWidget(self.laser1_status, 0, 1)
        self.laser_box_grid.addWidget(self.laser2_status, 1, 1)
        self.setLayout(self.laser_box_grid)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.laser_selection.buttonClicked.connect(
            lambda: self.tabmanager.update_current_laser(self.laser_selection.checkedId())
        )







