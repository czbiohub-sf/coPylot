from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QGroupBox,
    QGridLayout,
    QSizePolicy,
    QWidget,
    QVBoxLayout,
    QButtonGroup,
)


from copylot.gui._qt.photom_control.utils.labeledslider import LabeledSlider
from copylot.gui._qt.photom_control.utils.update_dac import signal_to_dac, signal_to_galvo

"""
This script creates the content for the laser control tab.
"""

class SimpleLaser(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.laser1_power = 0
        self.laser2_power = 0
        self.laser1_Wrange = (0, 100)  # 405nm laser: 0-100 mW
        self.laser2_Wrange = (0, 50)  # 785nm laser: 0-50 mW
        self.laser1_Vrange = parent.parent.vout_range[2]  # 405nm laser: 0-5 V
        self.laser2_Vrange = parent.parent.vout_range[3]  # 785nm laser: 0-5 V
        self.laser_power_list = [self.laser1_power, self.laser2_power]
        self.laser_Wrange_list = [self.laser1_Wrange, self.laser2_Wrange]
        self.laser_Vrange_list = [self.laser1_Vrange, self.laser2_Vrange]

        # Slide bars to control laser power
        self.laser1_power_indicator = QLabel(str(self.laser1_power))
        self.laser1_power_slider = LabeledSlider(self.laser1_Wrange[0], self.laser1_Wrange[1], 10)
        self.laser1_power_slider.sl.valueChanged.connect(self.update_laser_power)
        self.laser2_power_indicator = QLabel(str(self.laser2_power))
        self.laser2_power_slider = LabeledSlider(self.laser2_Wrange[0], self.laser2_Wrange[1], 5)
        self.laser2_power_slider.sl.valueChanged.connect(self.update_laser_power)

        # Laser switch
        self.laser1_switch = QPushButton('Off')
        self.laser2_switch = QPushButton('Off')
        self.laser1_switch.setCheckable(True)
        self.laser2_switch.setCheckable(True)
        self.laser1_switch.clicked[bool].connect(lambda: self.update_laser_onoff(0))
        self.laser2_switch.clicked[bool].connect(lambda: self.update_laser_onoff(1))
        self.laser_switch_gp = QButtonGroup()
        self.laser_switch_gp.setExclusive(False)
        self.laser_switch_gp.addButton(self.laser1_switch, 0)
        self.laser_switch_gp.addButton(self.laser2_switch, 1)
        self.init_laser()

        # Create a group box for each laser
        gpbox405 = QGroupBox('405nm Laser')
        gpbox405.setStyleSheet('font-size: 14pt')
        gpbox405.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        # font = QFont()
        # font.setPointSize(18)
        # gpbox405.setFont(font)
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(self.laser1_power_indicator, 0, 0)
        grid.addWidget(self.laser1_switch, 0, 1)
        grid.addWidget(self.laser1_power_slider, 1, 0, 1, 2)
        grid.setAlignment(Qt.AlignCenter)
        gpbox405.setLayout(grid)
        # gpbox405.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        gpbox785 = QGroupBox('785nm Laser')
        gpbox785.setStyleSheet('font-size: 14pt')
        # gpbox785.setFont(font)
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(self.laser2_power_indicator, 0, 0)
        grid.addWidget(self.laser2_switch, 0, 1)
        grid.addWidget(self.laser2_power_slider, 1, 0, 1, 2)
        grid.setAlignment(Qt.AlignCenter)
        gpbox785.setLayout(grid)

        # initialize DAC board
        self.update_laser_power()

        # Set layout
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setContentsMargins(5, 0, 5, 0)
        self.layout.addWidget(gpbox405)
        self.layout.addWidget(QLabel())
        self.layout.addWidget(gpbox785)
        self.setLayout(self.layout)

    def update_laser_power(self):
        self.laser1_power = self.laser1_power_slider.sl.value()
        self.laser2_power = self.laser2_power_slider.sl.value()
        self.laser_power_list = [self.laser1_power, self.laser2_power]
        self.laser1_power_indicator.setText('Power: ' + str(self.laser1_power) + ' mW')
        self.laser2_power_indicator.setText('Power: ' + str(self.laser2_power) + ' mW')
        if self.laser1_switch.isChecked():
            signal_to_dac(
                self.parent.parent.ao_range,
                self.laser1_power,
                self.laser1_Wrange,
                self.laser1_Vrange,
                dac_ch=self.parent.parent.laser405,
                invert=False,
            )
        if self.laser2_switch.isChecked():
            signal_to_dac(
                self.parent.parent.ao_range,
                self.laser2_power,
                self.laser2_Wrange,
                self.laser2_Vrange,
                dac_ch=self.parent.parent.laser785,
                invert=False,
            )

    def update_laser_onoff(self, laser_ind=None, laser_escape=True):
        """
        Update on/off state of the laser switch
        :param laser_ind: update the state of laser_ind
        :param laser_escape: move laser ouf of FOV
        """
        self.update_laser_power()
        if laser_ind is None:
            laser_list = range(2)
        else:
            laser_list = [laser_ind]
        for ind in laser_list:
            signal_to_dac(
                self.parent.parent.ao_range,
                self.laser_power_list[ind] if self.laser_switch_gp.buttons()[ind].isChecked() else 0,
                self.laser_Wrange_list[ind],
                self.laser_Vrange_list[ind],
                dac_ch=self.parent.parent.channel_list[ind + 2],
                invert=False,
            )
            if self.laser_switch_gp.buttons()[ind].isChecked():
                self.laser_switch_gp.buttons()[ind].setText('On')
            else:
                self.laser_switch_gp.buttons()[ind].setText('Off')

        # Escape laser point to out of FOV in safe mode
        if self.parent.parent.rb_safemode.isChecked() and laser_escape:
            if any([i.isChecked() for i in self.laser_switch_gp.buttons()]):
                x, y = self.parent.parent.window1.getMarkerCenter(self.parent.parent.window1.marker)
                self.parent.parent.window1.moveMarker(x, y, with_dac=True)
            else:
                signal_to_galvo(
                    self.parent.parent.ao_range,
                    (0, 0),
                    dac_ch_x=self.parent.parent.channel_list[0],
                    dac_ch_y=self.parent.parent.channel_list[1],
                    board_num=self.parent.parent.board_num,
                    invert=True,
                )



    def init_laser(self):
        for laser_ind in range(2):
            signal_to_dac(
                self.parent.parent.ao_range,
                0,
                self.laser_Wrange_list[laser_ind],
                self.laser_Vrange_list[laser_ind],
                dac_ch=self.parent.parent.channel_list[laser_ind + 2],
                invert=False,
            )
