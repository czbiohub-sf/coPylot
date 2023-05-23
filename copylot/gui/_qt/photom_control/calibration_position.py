import os
from os.path import join, dirname, abspath

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QPushButton,
    QLabel,
    QWidget,
    QGridLayout,
    QGroupBox,
    QVBoxLayout,
    QLineEdit,
    QFileDialog,
    QGraphicsItem,
    QShortcut,
)

from copylot.gui._qt.photom_control.helper_functions.messagebox import MessageBox
from copylot.gui._qt.photom_control.helper_functions.laser_selection_box import (
    LaserSelectionBox,
)

# from copylot.gui._qt.photom_control.utils.mirror_utils import MirroScanPoints
# from copylot.gui._qt.photom_control.controllers.dac_controller.scan_points import ScanPoints
from copylot.gui._qt.photom_control.controllers.demo_controller.demo_scan import (
    DemoScanPoints,
)
from copylot.gui._qt.photom_control.controllers.non_dac_controller.scan_points import MirrorScanning
from datetime import datetime


timestamp = datetime.now().strftime('%Y%m%d')

# TODO: import with the DAC
# from dac_controller.scan import DACscan
# from dac_controller.scan_points import ScanPoints

from copylot import logger


# TODO: add a method to reset the corners of the trapezoid
# TODO modify the LaserSelection Box to automatically get values from copylot
class LaserPositionCalibration(QWidget):
    """
    A class obj for the laser spot calibration tab.
    """

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.controlpanel = self.parent.parent
        self.window1 = self.controlpanel.window1
        self.demo_mode = self.controlpanel.demo_mode
        self.target_marker = None  # target marker widget
        self.ref_markers = []  # markers to create a reference tetragon

        # import the mirrors
        self.mirror_0 = self.controlpanel.mirror_0

        # Create buttons & text boxes
        self.laser_selection_box = LaserSelectionBox(self.parent)
        self.reset2center = QPushButton('Center')
        self.loadpath_input = QLineEdit(
            join(self.controlpanel.savepath_configs, ''), self
        )
        self.browse_load = QPushButton('Browse', self)
        self.load_button = QPushButton('Load', self)
        self.browse_save = QPushButton('Browse', self)
        self.savepath_input = QLineEdit(
            join(self.controlpanel.savepath_configs, f'calibration.txt'), self
        )
        self.pb_start = QPushButton('Start', self)
        self.pb_apply = QPushButton('Apply', self)
        self.pb_revert = QPushButton('Revert', self)
        self.pb_finish = QPushButton('Finish/Save', self)

        # Construct the reset cursor box
        reset_box = QGroupBox('Reset cursor to the center.')
        reset_box.setStyleSheet('QGroupBox::title {font-size: 14pt;}')
        reset_box_grid = QGridLayout()
        reset_box_grid.addWidget(self.reset2center)
        reset_box.setLayout(reset_box_grid)

        # Construct the load box
        load_box = QGroupBox('Load previous calibration settings')
        load_box.setStyleSheet('QGroupBox::title {font-size: 14pt;}')
        load_box_grid = QGridLayout()
        load_box_grid.addWidget(self.loadpath_input, 0, 0)
        load_box_grid.addWidget(self.browse_load, 0, 1)
        load_box_grid.addWidget(self.load_button, 0, 2)
        load_box.setLayout(load_box_grid)

        # Construct calibration control panel
        calibration_box = QGroupBox('Start a new calibration')
        calibration_box.setStyleSheet('QGroupBox::title {font-size: 14pt;}')
        calibration_box_grid = QGridLayout()
        calibration_box_grid.addWidget(QLabel('Initialize calibration'), 0, 0)
        calibration_box_grid.addWidget(self.pb_start, 0, 1)
        calibration_box_grid.addWidget(QLabel('Apply calibration'), 1, 0)
        calibration_box_grid.addWidget(self.pb_apply, 1, 1)
        calibration_box_grid.addWidget(QLabel('Revert calibration'), 2, 0)
        calibration_box_grid.addWidget(self.pb_revert, 2, 1)
        calibration_box_grid.addWidget(QLabel('Calibration save path'), 3, 0)
        calibration_box_grid.addWidget(self.savepath_input, 4, 0)
        calibration_box_grid.addWidget(self.browse_save, 4, 1)
        calibration_box_grid.addWidget(QLabel('Finish & Save'), 5, 0)
        calibration_box_grid.addWidget(self.pb_finish, 5, 1)
        calibration_box.setLayout(calibration_box_grid)

        # Connect buttons
        self.pb_start.clicked.connect(self.window1.initWindowsize)
        self.pb_start.clicked.connect(self.initVout)
        self.pb_start.clicked.connect(self.start_scan)
        self.pb_apply.clicked.connect(self.apply_calib)
        self.pb_revert.clicked.connect(self.revert_calib)
        self.pb_finish.clicked.connect(self.stop_scan)
        self.reset2center.clicked.connect(self.initVout)
        self.browse_load.clicked.connect(self.open_loadialog)
        self.load_button.clicked.connect(self.load_affinematrix)
        self.browse_save.clicked.connect(self.open_savedialog)

        # Assign shortcut keys
        self.shortcut_refresh = QShortcut(QKeySequence('Ctrl+r'), self)
        self.shortcut_refresh.activated.connect(self.apply_calib)

        # Set layout
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setContentsMargins(5, 0, 5, 0)
        self.layout.setSpacing(20)
        self.layout.addWidget(self.laser_selection_box)
        self.layout.addWidget(reset_box)
        self.layout.addWidget(load_box)
        self.layout.addWidget(calibration_box)
        self.setLayout(self.layout)

        # Define attributes
        self.ref_rect_coord = []
        self.ctrl_rect_coord = []
        self.scan_path = []

        # TODO: Check this function
        self.initVout()  # assign the center of the window to (0, 0) volt
        if self.controlpanel.demo_mode:
            raise NotImplementedError
            pass
            # demo_laser = self.window1.initCircle(
            #     self.window1.canvas_width // 2, self.window1.canvas_height // 2, size=10
            # )
            # self.demo_controller = DemoScanPoints(
            #     controlpanel=self.controlpanel, demo_laser=demo_laser, sampling_rate=4
            # )
        else:
            if self.controlpanel.dac_mode:
                raise NotImplementedError
                # self.dac_controller = ScanPoints(self.controlpanel, sampling_rate=100)
            else:
                self.mirror_controller = MirrorScanning(self, self.mirror_0)

    def size2cord(self, size):
        x0y0 = (
            -size[0] / 2 + self.window1.offset_x,
            -size[1] / 2 + self.window1.offset_y,
        )
        x1y0 = (x0y0[0] + size[0], x0y0[1])
        x1y1 = (x0y0[0] + size[0], x0y0[1] + size[1])
        x0y1 = (x0y0[0], x0y0[1] + size[1])
        return x0y0, x1y0, x1y1, x0y1

    def initVout(self):
        """
        Initialize marker and laser spot to the center.
        offset_x & y are the coordinates of the center position in the window.
        """
        self.window1.initOffset()
        self.window1.moveMarker(
                self.window1.offset_x, self.window1.offset_y, self.window1.marker
        )
        logger.info(f'offset: {(self.window1.offset_x, self.window1.offset_y)}')

    def init_cord(self):
        initial_ref_size = (
            self.window1.canvas_width * 2 / 3,
            self.window1.canvas_height * 2 / 3,
        )
        #TODO: might want to change this parameter or make it available for the user in the GUI
        ctrl_rect_scaling = 20
        initial_ctrl_size = (
            self.window1.canvas_width / ctrl_rect_scaling,
            self.window1.canvas_height / ctrl_rect_scaling,
        )
        self.ref_rect_coord = self.size2cord(initial_ref_size)
        self.ctrl_rect_coord = self.size2cord(initial_ctrl_size)
        self.scan_path = [[i[j] for i in self.ctrl_rect_coord] for j in range(2)]

    def load_affinematrix(self):
        e = self.controlpanel.transform_list[
            self.controlpanel.current_laser
        ].loadmatrix(self.loadpath_input.text())
        if e is None:
            self.parent.update_calibration_status()
            logger.info('Calibration loaded successfully.')
        else:
            logger.info(e, 'red')

    def open_loadialog(self):
        dlg = QFileDialog()
        dlg.setDirectory(self.loadpath_input.text())
        dlg.setNameFilter('*.txt')
        if dlg.exec_():
            filename = dlg.selectedFiles()[0]
            self.loadpath_input.setText(filename)
            self.load_affinematrix()

    def open_savedialog(self):
        dlg = QFileDialog()
        dlg.setDirectory(dirname(self.savepath_input.text()))
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        laser_num = self.controlpanel.current_laser
        if dlg.exec_():
            filepath = dlg.selectedFiles()[0]
            self.savepath_input.setText(filepath)
            if self.controlpanel.transform_list[laser_num].affmatrix is not None:
                savepath = self.check_savepath()
                self.controlpanel.transform_list[laser_num].savematrix(
                    filename=savepath
                )

    def check_savepath(self):
        if self.savepath_input.text()[-4:] == '.txt':
            savepath = self.savepath_input.text()
            os.makedirs(dirname(savepath), exist_ok=True)
            logger.info(
                f'Calibration is saved as {abspath(savepath)}',
            )
        else:
            savepath = f'{timestamp}_calibration_laser_{self.controlpanel.current_laser}.txt'
            logger.info(
                'Save path is not a txt file. \n'
                + f'Calibration is saved as {join(os.getcwd(), savepath)}',
                'red',
            )
        return savepath

    def size2cord(self, size):
        x0y0 = (
            -size[0] / 2 + self.window1.offset_x,
            -size[1] / 2 + self.window1.offset_y,
        )
        x1y0 = (x0y0[0] + size[0], x0y0[1])
        x1y1 = (x0y0[0] + size[0], x0y0[1] + size[1])
        x0y1 = (x0y0[0], x0y0[1] + size[1])
        return x0y0, x1y0, x1y1, x0y1

    def start_scan(self):
        self.window1.initWindowsize()
        self.init_cord()
        logger.info('Calibration has started.')
        # Hide the red/central marker
        self.window1.marker.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.window1.marker.setOpacity(0)
        self.window1.iscalib = True
        self.window1.initMarkerlist(self.ref_rect_coord, self.ctrl_rect_coord)
        self.window1.drawTetragon(self.ref_rect_coord)
        self.controlpanel.transform_list[
            self.controlpanel.current_laser
        ].affmatrix = None
        self.parent.update_calibration_status()
        if self.demo_mode:
            self.window1.start_laser_demo()

            # self.demo_controller.trans_obj = self.controlpanel.transform_list[
            #     self.controlpanel.current_laser
            # ]
            # # apply transformation if calibration has been done.
            # data_trans = self.demo_controller.trans_obj.affineTrans(
            #     self.ctrl_rect_coord
            # )
            # logger.info(f'coord transformed: {data_trans}')
            # logger.info(f'coord transformed: {data_trans}')

            # Start scan
            # self.demo_controller.start_scan()

        else:
            if self.controlpanel.dac_mode:
                # self.dac_controller.start_scan(self.ctrl_rect_coord)
                # self.dac_controller.trans_obj = self.controlpanel.transform_list[self.controlpanel.current_laser]
                # self.dac_controller.transfer2dac(self.ctrl_rect_coord)
                # self.dac_controller.start_scan()
                raise NotImplementedError("DAC Controller scanning not implemented")
            else:
                logger.debug('Start Scan')
                # raise NotImplementedError("No DAC ScanPoint not implemented")
                #Convert from coords to mirror by normalizing
                logger.info(f'ctrlrect {self.ctrl_rect_coord}')
                self.mirror_controller.start_scan(self.scan_path)

    def apply_calib(self):
        if self.window1.iscalib:
            self.ref_rect_coord, self.ctrl_rect_coord = self.collect_cord()
            self.controlpanel.transform_list[
                self.controlpanel.current_laser
            ].getAffineMatrix(*self.collect_cord())
            if self.demo_mode:
                # self.demo_controller.apply_matrix = True
                raise NotImplementedError("Apply calib demo not implemented")
            else:
                if self.controlpanel.dac_mode:
                    raise NotImplementedError(
                        "DAC Controller apply calib not implemented"
                    )
                    # self.dac_controller.trans_obj = self.controlpanel.transform_list[self.controlpanel.current_laser]
                    # self.dac_controller.apply_matrix = True

                else:
                    self.mirror_controller.trans_obj = self.controlpanel.transform_list[
                        self.controlpanel.current_laser
                    ]
                    # self.mirror_controller.trans_obj.affineTrans(self.ctrl_rect_coord)
                    self.mirror_controller.apply_matrix = True
                    logger.info('calib nondac applied')
                logger.info('Calibration has been applied.')

    def revert_calib(self):
        if self.demo_mode:
            # self.demo_controller.apply_matrix = False
            pass
            logger.warning("demo revert calib not implemented")
        else:
            if self.controlpanel.dac_mode:
                raise NotImplementedError("DAC Controller scanning not implemented")
                # self.dac_controller.apply_matrix = False
            else:
                self.mirror_controller.apply_matrix = False

        logger.info('Calibration is not applied.')

    def stop_scan(self):
        logger.info('Calibration has finished.')
        self.window1.marker.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.window1.stop_laser_demo()
        self.window1.marker.setOpacity(1)
        self.window1.iscalib = False
        self.window1.clearMarkerlist()
        self.parent.update_calibration_status()

        if self.demo_mode:
            # self.demo_controller.stop_scan()
            self.window1.stop_laser_demo()
        else:
            if self.controlpanel.dac_mode:
                raise NotImplementedError("DAC Controller scanning not implemented")
                # self.dac_controller.stop_scan()
            else:
                self.mirror_controller.stop_scan()

        # save affine matrix
        savepath = self.check_savepath()
        try:
            self.controlpanel.transform_list[
                self.controlpanel.current_laser
            ].savematrix(filename=savepath)
        except ValueError as e:
            logger.info('Calibration is not saved.\n' + str(e))

    def collect_cord(self):
        """
        Get 3 coordiantes from the reference rectangle
        and the adjusted/calibratino coordiantes.

        """
        ref_cord = [
            self.window1.getMarkerCenter(mk)
            for mk in self.controlpanel.window1.ref_marker_list
        ]
        ctrl_cord = [
            self.window1.getMarkerCenter(mk)
            for mk in self.controlpanel.window1.ctrl_marker_list
        ]
        logger.info(f'ref_cord {ref_cord} , ctrl_cord {ctrl_cord}')
        return ref_cord, ctrl_cord
