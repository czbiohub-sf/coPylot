import math

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QButtonGroup,
    QRadioButton,
    QLineEdit,
    QGroupBox,
    QGridLayout,
    QProgressBar,
    QApplication,
)

# from dac_controller.scan import DACscan
from copylot.gui._qt.photom_control.scan_algrthm.scan_algorithm import ScanAlgorithm
from copylot import logger
class DrawPatternUnit(QGroupBox):
    def __init__(self, title, tabmanager):
        super().__init__()
        self.title = title
        self.tabmanager = tabmanager
        self.window = tabmanager.parent.window1
        self.rb_group = QRadioButton(title, self)
        self.rb_lsj = QRadioButton('Lissajous', self)
        self.rb_rst = QRadioButton('Raster', self)
        self.rb_spr = QRadioButton('Spiral', self)
        self.verticalsize_input = QLineEdit(self)
        self.horizontalsize_input = QLineEdit(self)
        self.gap_input = QLineEdit('1', self)
        self.speed_input = QLineEdit('1', self)
        self.cyl_input = QLineEdit('1', self)
        self.prgbar = QProgressBar(self)
        self.prgbar.setStyleSheet('width: 100px;')
        self.prgbar.setAlignment(Qt.AlignCenter)
        self.pb_preview = QPushButton('Preview')
        self.pb_preview.setCheckable(True)
        self.pb_start = QPushButton('Start')
        self.pb_pause = QPushButton('Pause')
        self.pb_stop = QPushButton('Stop')
        self.stop_draw_flag = False
        self.pause_draw_flag = False
        self.draw_inprogress_flag = False
        self.external_draw_list = None
        self.current_prog = 0
        self.scanobj = None
        self.scan_path = None
        self.size_par = None
        self.cycl_par = None
        self.gap_par = None
        self.speed_par = None
        self.marker_pos0 = self.window.getMarkerCenter(self.window.marker)
        self.dac_controller = None

        # ButtonGroups for scanning algorithm
        self.bg_scan = QButtonGroup(self)
        self.bg_scan.addButton(self.rb_lsj, 0)
        self.bg_scan.addButton(self.rb_rst, 1)
        self.bg_scan.addButton(self.rb_spr, 2)
        self.bg_scan.buttons()[self.tabmanager.parent.current_scan_pattern].setChecked(True)

        # Construct grid layout
        # self.setStyleSheet('font-size: 12pt')
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        grid.addWidget(self.rb_group, 0, 0)
        grid.addWidget(self.pb_preview, 0, 2)
        grid.addWidget(QLabel('Size (V, H)'), 1, 0)
        grid.addWidget(self.verticalsize_input, 1, 1)
        grid.addWidget(self.horizontalsize_input, 1, 2)
        grid.addWidget(QLabel('Interval'), 2, 0)
        grid.addWidget(self.gap_input, 2, 1)
        grid.addWidget(QLabel('pixels'), 2, 2)
        grid.addWidget(QLabel('Speed'), 3, 0)
        grid.addWidget(self.speed_input, 3, 1)
        grid.addWidget(QLabel('sec/cycle'), 3, 2)
        grid.addWidget(QLabel('Cycle'), 4, 0)
        grid.addWidget(self.cyl_input, 4, 1)
        grid.addWidget(QLabel('times'), 4, 2)
        grid.addWidget(self.rb_lsj, 5, 0)
        grid.addWidget(self.rb_rst, 5, 1)
        grid.addWidget(self.rb_spr, 5, 2)
        grid.addWidget(self.prgbar, 6, 0, 1, 3)
        grid.addWidget(self.pb_start, 7, 0)
        grid.addWidget(self.pb_pause, 7, 1)
        grid.addWidget(self.pb_stop, 7, 2)
        grid.setAlignment(Qt.AlignCenter)
        self.setLayout(grid)

        # Linking buttons to functions
        self.pb_preview.clicked.connect(self.preview)
        self.pb_start.clicked.connect(self.start_scan)
        self.pb_stop.clicked.connect(self.stop_scan)
        self.pb_pause.clicked.connect(self.pause_scan)
        self.bg_scan.buttonClicked.connect(
            lambda: self.tabmanager.update_scan_pattern(self.bg_scan.checkedId()) if self.rb_group.isChecked() else None
        )

    def print_log(self, obj=None):
        for i in obj.buttons():
            if i.isChecked():
                print(i.text() + f' pattern is selected.')

    def centerMarker2scanregion(self):
        self.marker_pos0 = (self.window.scanregion.center().x(), self.window.scanregion.center().y())
        self.window.moveMarker(self.marker_pos0[0], self.marker_pos0[1], self.window.marker)

    def start_scan(self):
        """
        Start scanning.
        """
        if self.checkstatus():
            self.centerMarker2scanregion()
            self.disable_buttons([self.pb_start, self.pb_pause, self.pb_stop])
            logger.info(f'Scan {self.title} initiated.')
            self.stop_draw_flag = False
            self.draw_inprogress_flag = True
            if not self.pause_draw_flag:
                self.current_prog = 0
                self.select_algorithm()
                if not self.window.parent.demo_mode:
                    logger.info(f'Transferring data to DAC board...')
                    # self.dac_controller = DACscan(self.scan_path, self.tabmanager.parent)
                    # self.dac_controller.trans_obj = self.tabmanager.parent.transform_list[
                    #     self.tabmanager.parent.current_laser
                    # ]
                    # self.dac_controller.transfer2dac()
            self.pause_draw_flag = False
            logger.info(f'Scanning {self.title} ...')
            if self.window.parent.demo_mode:
                self.enable_buttons([self.pb_start, self.pb_pause, self.pb_stop])
                steps_per_cycle = len(self.scan_path[0])
                total_steps = steps_per_cycle * self.cycl_par
                while self.current_prog < total_steps:
                    QApplication.processEvents()
                    if self.stop_draw_flag or self.pause_draw_flag:
                        break
                    else:
                        self.window.moveMarker(self.scan_path[0][self.current_prog % steps_per_cycle],
                                               self.scan_path[1][self.current_prog % steps_per_cycle],
                                               self.window.marker)
                        # time.sleep(1e-5)  # max sampling rate of DAC is 100kS/s
                        self.prgbar.setValue(self.current_prog)
                        self.current_prog += 1
                if not self.pause_draw_flag:
                    self.resetMarkerPosition()
            else:
                self.dac_controller.start_scan()
                self.enable_buttons([self.pb_pause, self.pb_stop])
                self.dac_controller.update_values(self.window, self.prgbar)
            print('scanning process finished.')
            self.draw_inprogress_flag = False
            print('scan_inprogress_flag turned False')
            if not self.pause_draw_flag:
                print('resetting Marker Poisition...')
                self.resetMarkerPosition()
                print('Marker position reset.')
            if (
                    not self.pause_draw_flag
                    and not self.stop_draw_flag
            ):
                logger.info(f'Scanning {self.title} has completed.')
            self.enable_buttons([self.pb_start])
            QApplication.processEvents()

    def pause_scan(self):
        """
        Pausing scanning. Can restart scan from the same point.
        """
        if self.draw_inprogress_flag:
            self.pause_draw_flag = True
            self.disable_buttons([self.pb_start, self.pb_pause, self.pb_stop])
            if not self.window.parent.demo_mode:
                curr_count, curr_index = self.dac_controller.pause_scan()
                print(f'pausing at index: {curr_index}')
                self.scan_path = self.trimdata(self.scan_path, curr_index // 2)
                self.dac_controller.transfer2dac(self.scan_path)
            logger.info(f'Pausing scanning {self.title}.')
            self.enable_buttons([self.pb_start, self.pb_pause, self.pb_stop])

    def stop_scan(self):
        """
        Stop scanning. Progress will be reset.
        """
        if self.draw_inprogress_flag:
            self.disable_buttons([self.pb_start, self.pb_pause, self.pb_stop])
            if not self.window.parent.demo_mode:
                self.dac_controller.stop_scan()
            self.enable_buttons([self.pb_start, self.pb_pause, self.pb_stop])

        self.stop_draw_flag = True
        self.pause_draw_flag = False
        self.draw_inprogress_flag = False
        self.current_prog = 0
        self.prgbar.setValue(self.current_prog)
        self.resetMarkerPosition()
        logger.info(f'Scanning {self.title} has stopped.')

    def checkstatus(self):
        """
        Safty check before start scanning
        """
        logger.info(f'Checking status ...')
        if not self.rb_group.isChecked():
            logger.info(f'{self.title} pattern is not selected. \nPlease select the pattern.')
            return False
        if any([i.draw_inprogress_flag for i in self.external_draw_list]):
            logger.info('Other pattern is scanning now. \nPlease stop it or wait until it ends.')
            return False
        else:
            try:
                self.size_par = (float(self.verticalsize_input.text()), float(self.horizontalsize_input.text()))
            except:
                logger.info(f'Invalid input in Size. \nInterval value must be a number.')
                return False
            try:
                self.cycl_par = float(self.cyl_input.text())
                # if self.cycl_par != float(self.cyl_input.text()):
                #     logger.info(f'Cycle is rounded to {self.cycl_par}.')
            except:
                logger.info(f'Invalid input in Cycle. \nInterval value must be an integer.')
                return False
            try:
                self.gap_par = float(self.gap_input.text())
            except:
                logger.info('Invalid input in Interval. \nInterval value must be a number.')
                return False
            try:
                self.speed_par = float(self.speed_input.text())
            except:
                logger.info('Invalid input in Speed. \nInterval value must be a number.')
                return False
            try:
                ScanAlgorithm(self.marker_pos0, self.size_par, self.gap_par, self.title, self.speed_par, )
            except ValueError as e:
                logger.info(str(e))
                return False
            return True

    def select_algorithm(self, position=None):
        """
        Select scanning algorithm. Scanning data will be created in self.scan_path.
        """
        logger.info(f'Selecting algorithm ...')
        if position is None:
            self.marker_pos0 = self.window.getMarkerCenter(self.window.marker)
        else:
            self.marker_pos0 = position
        self.scanobj = ScanAlgorithm(
            self.marker_pos0,
            self.size_par,
            self.gap_par,
            self.title,
            self.speed_par,
        )
        print('Scan with ' + self.bg_scan.buttons()[self.bg_scan.checkedId() - 1].text())
        if self.bg_scan.checkedId() == 0:
            self.scan_path = self.scanobj.generate_lissajous()
        elif self.bg_scan.checkedId() == 1:
            self.scan_path = self.scanobj.generate_sin()
        elif self.bg_scan.checkedId() == 2:
            self.scan_path = self.scanobj.generate_spiral()
        print(f'total number of points {len(self.scan_path[0])}')
        self.prgbar.setMaximum(len(self.scan_path[0]) * self.cycl_par)

    def resetMarkerPosition(self):
        """
        Reset Marker & laser point to the starting position.
        """
        self.window.moveMarker(self.marker_pos0[0], self.marker_pos0[1], self.window.marker, with_dac=True)
        QApplication.processEvents()

    def trimdata(self, data, index):
        """
        Trim data array at where the scan posed so that scan can resume from the paused position.
        :param data: a data list all channel
        :param index: index paused at
        :return: rotated data list
        """
        data_list = []
        for data_ch in data:
            data_list.append(data_ch[index + 1:])
        return data_list

    def disable_buttons(self, button_list):
        [b.setEnabled(False) for b in button_list]
        self.repaint()

    def enable_buttons(self, button_list):
        [b.setEnabled(True) for b in button_list]
        self.repaint()

    def preview(self):
        if self.pb_preview.isChecked():
            if self.checkstatus():
                print(f'H: {self.window.scanregion.height()}, W: {self.window.scanregion.width()}')
                self.select_algorithm((self.window.scanregion.center().x(), self.window.scanregion.center().y()))
                self.window.draw_preview(self.scan_path)
                logger.info('Showing preview of scanning path.')
        else:
            self.window.clear_preview()
            logger.info('')
