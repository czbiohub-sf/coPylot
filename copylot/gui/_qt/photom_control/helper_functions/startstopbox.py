from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QGroupBox,
    QGridLayout,
    QProgressBar,
    QApplication,
)

# from dac_controller.scan import DACscan
from copylot.gui._qt.photom_control.scan_algrthm.scan_algorithm import ScanAlgorithm
# from copylot.gui._qt.photom_control.utils.mirror_utils import ScanPoints

from copylot import logger

class StartStop(QGroupBox):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.controlpanel = parent.parent.parent
        self.mirror_0 = self.controlpanel.mirror_0

        # QT components
        self.prgbar_intra = QProgressBar(self)
        self.prgbar_inter = QProgressBar(self)
        self.pb_start = QPushButton('Start')
        self.pb_pause = QPushButton('Pause')
        self.pb_stop = QPushButton('Stop')
        self.pb_preview = QPushButton('Preview')
        self.pb_preview.setCheckable(True)

        self.setTitle('Scan multi-region')
        # self.setStyleSheet('font-size: 14pt')
        grid = QGridLayout()
        grid.addWidget(QLabel('Intraregion'), 0, 0)
        grid.addWidget(self.prgbar_intra, 0, 1, 1, 3)
        grid.addWidget(QLabel('Interregion'), 1, 0)
        grid.addWidget(self.prgbar_inter, 1, 1, 1, 3)
        grid.addWidget(self.pb_start, 2, 0)
        grid.addWidget(self.pb_pause, 2, 1)
        grid.addWidget(self.pb_stop, 2, 2)
        grid.addWidget(self.pb_preview, 2, 3)
        self.setLayout(grid)

        # Connect buttons to functions
        self.pb_start.clicked.connect(self.start_scan)
        self.pb_pause.clicked.connect(self.pause_scan)
        self.pb_stop.clicked.connect(self.stop_scan)
        self.pb_preview.clicked.connect(self.draw_preview)

        # Placeholders
        self.scanobj_list = []  # a list to store scanobj for each region
        self.stop_scan_flag = False  # a flag to stop scanning
        self.pause_scan_flag = False  # a flag to pause scanning
        self.scan_inprogress_flag = False  # a flag indicating scan is running
        self.dac_controller = None
        self.curr_intra = 0  # current index of intraregion progress
        self.curr_inter = 0  # current index of interregion progress
        self.curr_scan_path = None  # current scan path

    def collect_scanobj(self):
        """
        Create a list of scanobj cylce and algorithm.
        :return: True if all scanobj are correctly collected. Otherwise False.
        """
        self.scanobj_list = []
        for row in range(self.parent.bg_table.tableWidget.rowCount()):
            par = self.collect_row(row)
            if par:
                self.scanobj_list.append([ScanAlgorithm(*(par[1:4] + par[0:1] + par[4:5]))] + par[-3:-1])
            else:
                return False
        return True

    def start_scan(self):
        if self.collect_scanobj():
            self.disable_buttons([self.pb_start, self.pb_pause, self.pb_stop])
            logger.info(f'Scan initiated.')
            self.stop_scan_flag = False
            self.scan_inprogress_flag = True
            if not self.pause_scan_flag:
                self.curr_inter = 0
                self.prgbar_inter.setMaximum(len(self.scanobj_list))
            while self.curr_inter < len(self.scanobj_list):
                QApplication.processEvents()
                scan = self.scanobj_list[self.curr_inter]
                if not self.pause_scan_flag:
                    self.curr_scan_path = self.generate_scanpath_perregion(scan[0], scan[-1])
                    self.curr_intra = 0
                    self.prgbar_inter.setValue(self.curr_inter)
                    self.prgbar_intra.setMaximum(len(self.curr_scan_path[0]) * scan[-2])
                if not self.controlpanel.demo_mode:
                    if self.controlpanel.dac_mode:
                        raise NotImplementedError("DAC Controller scanning not implemented")
                        # # Transfer data to DAC board
                        # logger.info(f'Transferring data #{self.curr_inter} to DAC board...')
                        # if not self.pause_scan_flag:
                        #     self.dac_controller = DACscan(self.curr_scan_path, self.controlpanel)
                        #     self.dac_controller.trans_obj = self.controlpanel.transform_list[
                        #         self.controlpanel.current_laser
                        #     ]
                        #     self.dac_controller.transfer2dac()
                    else:
                        if not self.pause_scan_flag:
                            # self.mirror_controller = ScanPoints(self, self.mirror_0)
                            # self.mirror_controller.trans_obj = self.controlpanel.transform_list[
                            #     self.controlpanel.current_laser
                            # ]        
                            raise NotImplementedError                    
                self.pause_scan_flag = False
                logger.info(f'Scanning #{self.curr_inter} region...')

                if self.controlpanel.demo_mode:
                    self.enable_buttons([self.pb_start, self.pb_pause, self.pb_stop])
                    steps_per_cycle = len(self.curr_scan_path[0])
                    total_steps = steps_per_cycle * scan[-2]
                    while self.curr_intra < total_steps:
                        QApplication.processEvents()
                        if self.stop_scan_flag or self.pause_scan_flag:
                            break
                        else:
                            self.controlpanel.window1.moveMarker(
                                self.curr_scan_path[0][self.curr_intra % steps_per_cycle],
                                self.curr_scan_path[1][self.curr_intra % steps_per_cycle],
                                self.controlpanel.window1.marker
                            )
                            self.curr_intra += 1
                            self.prgbar_intra.setValue(self.curr_intra)
                else:
                    self.dac_controller.start_scan()
                    self.enable_buttons([self.pb_pause, self.pb_stop])
                    self.dac_controller.update_values(
                        self.controlpanel.window1,
                        self.prgbar_intra,
                        laser_escape=True if self.curr_inter == len(self.scanobj_list) - 1 else False
                    )
                if self.stop_scan_flag or self.pause_scan_flag:
                    break
                self.curr_inter += 1
                self.prgbar_inter.setValue(self.curr_inter)

            print('scanning process finished.')
            self.scan_inprogress_flag = False
            if not self.pause_scan_flag and not self.stop_scan_flag:
                logger.info(f'Scan has completed.')
            self.enable_buttons([self.pb_start])

    def pause_scan(self):
        """
        Pausing scanning. Can restart scan from the same point.
        """
        if self.scan_inprogress_flag:
            self.pause_scan_flag = True
            self.disable_buttons([self.pb_start, self.pb_pause, self.pb_stop])
            if not self.controlpanel.demo_mode:
                curr_count, curr_index = self.dac_controller.pause_scan()
                print(f'pausing at index: {curr_index}')
                self.curr_scan_path = self.trimdata(self.curr_scan_path, curr_index // 2)
                self.dac_controller.transfer2dac(self.curr_scan_path)
            logger.info(f'Pausing scanning.')
            self.enable_buttons([self.pb_start, self.pb_pause, self.pb_stop])

    def stop_scan(self):
        """
        Stop scanning. Progress will be reset.
        """
        if self.scan_inprogress_flag:
            self.disable_buttons([self.pb_start, self.pb_pause, self.pb_stop])
            if not self.controlpanel.demo_mode:
                self.dac_controller.stop_scan()
            self.enable_buttons([self.pb_start, self.pb_pause, self.pb_stop])
        self.stop_scan_flag = True
        self.pause_scan_flag = False
        self.scan_inprogress_flag = False
        self.curr_intra = 0
        self.curr_inter = 0
        self.prgbar_intra.setValue(self.curr_intra)
        self.prgbar_inter.setValue(self.curr_inter)
        logger.info(f'Scan stopped.')

    def draw_preview(self):
        if self.pb_preview.isChecked():
            logger.info('Generating scan path...')
            if self.collect_scanobj():
                scan_path_all_x = []
                scan_path_all_y = []
                for i, scan in enumerate(self.scanobj_list):
                    scan_path = self.generate_scanpath_perregion(scan[0], scan[-1])
                    scan_path_all_x += scan_path[0]
                    scan_path_all_y += scan_path[1]
                self.controlpanel.window1.draw_preview((scan_path_all_x, scan_path_all_y))
                logger.info('Showing preview of scanning path.')
        else:
            self.controlpanel.window1.clear_preview('all')
            logger.info('')

    def collect_row(self, row):
        """
        Verify input values of one row
        :param row: row index
        :return: False if any param is no good, otherwise True
        """
        table = self.parent.bg_table.tableWidget
        msg = []
        par = []
        stop = False
        for col in range(table.columnCount()):
            item = table.item(row, col)
            if col == 0:
                if item.text() in ('Rect', 'Disk'):
                    par.append(item.text())
                else:
                    msg.append(
                        f'Invalid value in row {row + 1}, {table.horizontalHeaderItem(col).text()}.'
                        '\nInput Rect or Disk.',
                    )
                    stop = True
            elif 1 <= col < 3:
                stop0 = False
                try:
                    v = eval(item.text())
                    if not isinstance(v, tuple) or len(v) != 2:
                        stop0 = True
                    else:
                        par.append(v)
                except:
                    stop0 = True
                if stop0:
                    msg.append(
                        f'Invalid value in row {row + 1}, {table.horizontalHeaderItem(col).text()}.'
                        '\nInput 2 numerical values separated by ,.',
                    )
                    stop = True
            elif 3 <= col < 6:
                try:
                    par.append(eval(item.text()))
                except:
                    msg.append(
                        f'Invalid value in row {row + 1}, {table.horizontalHeaderItem(col).text()}.'
                        '\nInput 1 numerical value.',
                    )
                    stop = True
            elif col == 6:
                if item.text() in ('Lissajous', 'Raster', 'Spiral'):
                    par.append(item.text())
                else:
                    msg.append(
                        f'Invalid value in row {row + 1}, {table.horizontalHeaderItem(col).text()}.'
                        '\nInput Lissajous, Raster or Spiral.',
                    )
                    stop = True
            else:
                par.append(item.text())
        if stop:
            logger.info('\n'.join(msg), 'red')
        else:
            return par

    def generate_scanpath_perregion(self, scanobj, algorithm):
        """
        Return scan_path with scanobj and algorithm.
        """
        logger.info(f'Selecting algorithm ...')
        scan_path = ([], [])
        if algorithm == 'Lissajous':
            scan_path = scanobj.generate_lissajous()
        elif algorithm == 'Raster':
            scan_path = scanobj.generate_sin()
        elif algorithm == 'Spiral':
            scan_path = scanobj.generate_spiral()
        print(f'total number of points {len(scan_path[0])}')
        return scan_path

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

