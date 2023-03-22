from PyQt5.QtWidgets import (
    QTabWidget,
)
from copylot.gui._qt.photom_control.calibration_position import LaserPositionCalibration
# from copylot.gui._qt.photom_control.multi_pattern import MultiPatternControl
# from widgets.simple_laser import SimpleLaser
# from copylot.gui._qt.photom_control.pattern_control import PatternControl


class TabManager(QTabWidget):
    """
    A TabManager that manages multiple tabs.

    """
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # self.buttonSize = (200, 100)

        # Add contents for each tab
        self.laser_cali = LaserPositionCalibration(self)
        # self.simple_laser = SimpleLaser(self)
        # self.pattern_ctrl = PatternControl(self)
        # self.multi_pattern = MultiPatternControl(self)

        # Add tabs
        # self.addTab(self.simple_laser, 'Simple Laser')
        self.addTab(self.laser_cali, 'Calibration')
        # self.addTab(self.pattern_ctrl, 'Single Scan')
        # self.addTab(self.multi_pattern, 'Multi Scans')

    def update_current_laser(self, laser_idx):
        """
        To update current laser selection in the laser selection boxes.
        Since the laser selection box on each tab is an independent widget, laser selection update has to be controlled
        uniquely from tab manager.
        :param laser_idx: index of laser
        """
        self.parent.current_laser = laser_idx
        for i in range(self.count()):
            if hasattr(self.widget(i), 'laser_selection_box'):
                self.widget(i).laser_selection_box.laser_selection.buttons()[self.parent.current_laser].setChecked(True)

    def update_calibration_status(self):
        """
        To update calibration status in the laser selection boxes.
        Since the laser selection box on each tab is an independent widget, laser calibration status update has to be
        controlled uniquely from tab manager.
        """
        for i in range(self.count()):
            if hasattr(self.widget(i), 'laser_selection_box'):
                boxgrid = self.widget(i).laser_selection_box.laser_box_grid
                for laser_num in range(2):
                    if self.parent.transform_list[laser_num].affmatrix is None:
                        boxgrid.itemAtPosition(laser_num, 1).widget().setText('Not calibrated')
                        boxgrid.itemAtPosition(laser_num, 1).widget().setStyleSheet('color: gray')
                    else:
                        boxgrid.itemAtPosition(laser_num, 1).widget().setText('Calibration Done!')
                        boxgrid.itemAtPosition(laser_num, 1).widget().setStyleSheet('color: green')

    def update_scan_shape(self, ind):
        self.parent.current_scan_shape = ind
        self.pattern_ctrl.bg_pattern_selection.buttons()[ind].setChecked(True)
        self.multi_pattern.bg_indiv.bg_shape.buttons()[ind].setChecked(True)

    def update_scan_pattern(self, ind):
        self.parent.current_scan_pattern = ind
        unit = self.pattern_ctrl.get_pattern_unit()
        unit.bg_scan.buttons()[ind].setChecked(True)
        self.multi_pattern.bg_indiv.bg_scan.buttons()[ind].setChecked(True)





