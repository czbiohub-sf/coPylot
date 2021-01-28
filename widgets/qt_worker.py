import sys
import traceback
import logging
import time
import qt_worker_signals
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

logging.basicConfig(format="%(message)s", level=logging.INFO)


class Worker(QRunnable):
    def __init__(self, name, *args, **kwargs):
        super(Worker, self).__init__()
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.thread_active = True

        self.signals = qt_worker_signals.WorkerSignals()
        self.kwargs["finished_callback"] = self.signals.finished
        self.kwargs["interrupted_callback"] = self.signals.interrupted
        self.kwargs["progress_callback"] = self.signals.progress

    @pyqtSlot()
    def run(self):
        logging.info(f"{self.name} started")
        counter = 0
        while self.thread_active and counter < 10:
            time.sleep(0.5)
            counter += 1
            self.signals.progress.emit(counter)
        if counter == 10:
            self.signals.finished.emit()

    def stop(self):
        self.thread_active = False
        self.signals.interrupted.emit()

