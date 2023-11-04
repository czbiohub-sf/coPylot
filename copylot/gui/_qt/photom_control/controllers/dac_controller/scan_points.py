import threading
import time

from PyQt5.QtCore import QThreadPool

from widgets.utils.update_dac import signal_to_dac
from widgets.helper_functions.qthreadworker import Worker


class ScanPoints:
    def __init__(self, controlpanel, sampling_rate=100):
        """
        A class object for DAC scanning a pattern on its own buffer memory.
        :param controlpanel: Class object of ControlPanel
        :param sampling_rate: pseudo sampling to send signal to DAC board
        """
        self.controlpanel = controlpanel
        self.ch_list = controlpanel.channel_list
        self.num_chans = 2
        self.board_num = controlpanel.board_num
        self.sampling_rate = sampling_rate
        self.input_range_list = [(0, controlpanel.window1.canvas_width), (0, controlpanel.window1.canvas_height)]
        self.vout_range = controlpanel.galvo_x_range
        self.ao_range = controlpanel.ao_range
        self.trans_obj = controlpanel.transform_list[controlpanel.current_laser]
        self.data_list = []
        self.threadpool = QThreadPool()
        self.isrunning = False
        self.apply_matrix = False

    def exec_scan(self):
        self.trans_obj = self.controlpanel.transform_list[self.controlpanel.current_laser]
        self.input_range_list = [
            (0, self.controlpanel.window1.canvas_width), (0, self.controlpanel.window1.canvas_height)
        ]
        while self.controlpanel.window1.iscalib:
            self.isrunning = True
            if self.apply_matrix:
                scan_path = self.trans_obj.affineTrans(self.data_list)
                print('Affine transformed.')
            else:
                scan_path = self.data_list
            for x, y in zip(scan_path[0], scan_path[1]):
                signal_to_dac(
                    self.ao_range,
                    x,
                    value_range=self.input_range_list[0],  # range of output laser power
                    Vout_range=self.vout_range,
                    dac_ch=self.ch_list[0],
                    board_num=self.board_num,
                    invert=True,
                )
                signal_to_dac(
                    self.ao_range,
                    y,
                    value_range=self.input_range_list[1],  # range of output laser power
                    Vout_range=self.vout_range,
                    dac_ch=self.ch_list[1],
                    board_num=self.board_num,
                    invert=True,
                )
                time.sleep(1 / self.sampling_rate)
        self.isrunning = False

    def start_scan(self, data_list):
        self.data_list = data_list
        if self.isrunning:
            self.controlpanel.window1.iscalib = False
            self.threadpool.clear()
            while not self.threadpool.waitForDone():
                time.sleep(0.01)
        self.controlpanel.window1.iscalib = True
        worker = Worker(self.exec_scan)
        self.threadpool.start(worker)

    def stop_scan(self):
        self.controlpanel.window1.iscalib = False
        self.threadpool.clear()
        while not self.threadpool.waitForDone():
            time.sleep(0.01)
        # if self.thread is not None:
        #     self.thread.is_scanning = False
        #     self.thread.join()
