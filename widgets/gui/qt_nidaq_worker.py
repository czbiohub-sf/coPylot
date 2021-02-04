import sys
import traceback
import logging
import time
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from widgets.hardware.alternative_control import NIdaq
from widgets.hardware.control import NIDaq

logging.basicConfig(format="%(message)s", level=logging.INFO)


class NIDaqWorker(QRunnable):
    def __init__(self, parameters, view, channel, *args, **kwargs):
        super(NIDaqWorker, self).__init__()

        self.parameters = parameters
        self.view = int(view[5])
        self.channel = int(channel)
        self.args = args
        self.kwargs = kwargs

        self.thread_active = True

    @pyqtSlot()
    def run(self):
        logging.info(f"NIDaq Instance launched")
        # while True:
        #     time.sleep(1)
        #     logging.info(self.thread_active)
        #     if not self.thread_active:
        #         break
        self.daq_card = NIdaq(exposure=self.parameters[0],
                              nb_timepoints=self.parameters[1],
                              scan_step=self.parameters[2],
                              stage_scan_range=self.parameters[3],
                              vertical_pixels=self.parameters[4],
                              num_samples=self.parameters[5],
                              offset_view1=self.parameters[6],
                              offset_view2=self.parameters[7],
                              view1_galvo1=self.parameters[8],
                              view1_galvo2=self.parameters[9],
                              view2_galvo1=self.parameters[10],
                              view2_galvo2=self.parameters[11],
                              stripe_reduction_range=self.parameters[12],
                              stripe_reduction_offset=self.parameters[13])

        self.daq_card.select_view(1)
        self.daq_card.select_channel_remove_stripes(488)
        print("end of worker")

    def stop(self):
        print("nidaq_worker stop method called")
        self.thread_active = False
        self.daq_card.stop_now = True
        print("end of nidaq_worker stop method")

