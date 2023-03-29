from copylot.hardware.mirrors.optotune.mirror import OptoMirror
import time
from copylot.gui._qt.photom_control.helper_functions.qthreadworker import Worker
import logging

logger = logging.getLogger(__name__)

class ScanPoints:
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

    def start_scan(self, data_list):
        self.data_list = data_list
        if self.isrunning:
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
        while self.controlpanel.window1.iscalib:
            self.isrunning = True
            if self.apply_matrix:
                scan_path = self.trans_obj.affineTrans(self.data_list)
                print('Affine transformed.')
            else:
                scan_path = self.data_list
            for x, y in zip(scan_path[0], scan_path[1]):
                self.mirror.position_x = x
                self.mirror.position_y = y
                # time.sleep(1 / self.sampling_rate)
        self.isrunning = False
