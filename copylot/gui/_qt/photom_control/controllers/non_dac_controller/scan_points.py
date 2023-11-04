import time
from copylot.hardware.mirrors.optotune.mirror import OptoMirror
import time
from copylot.gui._qt.photom_control.helper_functions.qthreadworker import Worker
from copylot import logger
from PyQt5.QtCore import QThreadPool

from copylot.hardware.mirrors.optotune.mirror import OptoMirror
import time
from copylot.gui._qt.photom_control.helper_functions.qthreadworker import Worker
from copylot import logger
from copylot.gui._qt.photom_control.utils.conversion import value_converter


class MirrorScanning:
    def __init__(self, parent, mirror: OptoMirror):
        super().__init__()
        self.parent = parent
        self.tab_manager = self.parent.parent
        self.controlpanel = self.parent.parent.parent

        self.mirror = mirror
        self.threadpool = self.controlpanel.threadpool
        self.trans_obj = self.controlpanel.transform_list[
            self.controlpanel.current_laser
        ]
        self.is_running = False
        self.data_list = []
        self.apply_matrix = False

        self.input_range_list = [
            (0, self.controlpanel.window1.canvas_width),
            (0, self.controlpanel.window1.canvas_height),
        ]

        # TODO: ideally this should be a base property returned by the mirror.
        self.mirror_range = (-1.0, 1.0)
        self.mirro_resolution = 0.01     

    def start_scan(self, data_list):
        self.data_list = data_list.copy()
        # Rescale input coords to mirror coords
        if self.is_running:
            self.controlpanel.window1.iscalib = False
            self.threadpool.clear()
            while not self.threadpool.waitForDone():
                time.sleep(0.01)
        self.controlpanel.window1.iscalib = True
        worker = Worker(self.execute_scan)
        self.threadpool.start(worker)

    def stop_scan(self):
        self.threadpool.clear()
        while not self.threadpool.waitForDone():
            time.sleep(0.01)

    def execute_scan(self):
        self.trans_obj = self.controlpanel.transform_list[
            self.controlpanel.current_laser
        ]
        self.input_range_list = [
            (0, self.controlpanel.window1.canvas_width),
            (0, self.controlpanel.window1.canvas_height),
        ]
        logger.info(f'input range exec {self.input_range_list}')
        logger.info(f'transf_obj range exec {self.trans_obj}')

        while self.controlpanel.window1.iscalib:
            self.isrunning = True
            logger.info(f'data_list {self.data_list}')
            if self.apply_matrix:
                scan_path = self.trans_obj.affineTrans(self.data_list)
                logger.info(f'Affine transformed. {scan_path}')
                scan_path[0] = value_converter(scan_path[0], self.input_range_list[0], (-1.0, 1.0), invert=False)
                scan_path[1] = value_converter(scan_path[1], self.input_range_list[1], (-1.0, 1.0), invert=True)
                logger.info(f'Affine transformed rescaled: {scan_path}')

            else:
                print('no affine convert')
                scan_path = self.data_list.copy()
                scan_path[0] = value_converter(scan_path[0], self.input_range_list[0], (-1.0, 1.0), invert=False)
                scan_path[1] = value_converter(scan_path[1], self.input_range_list[1], (-1.0, 1.0), invert=True)

            logger.info(f'scanpath {scan_path}')
            for x, y in zip(scan_path[0], scan_path[1]):
                logger.info(f'position [{x},{y}]')
                self.mirror.position_x = x
                self.mirror.position_y = y
                time.sleep(1.0)  #Adding thsi much delay to have a chance to click the laser
        self.isrunning = False

    # def convert_coords(self, data_list=None, invert=False):
    #     # Apply the Affine Transform
    #     data_trans = self.trans_obj.affineTrans(data_list)
    #     self.data_list = [
    #         value_converter(data, inrng, self.mirror_range, invert=invert)
    #         for inrng, data in zip(self.input_range_list, data_trans)
    #     ]
    #     logger.info(f'Normalized coords: {self.data_list}')
