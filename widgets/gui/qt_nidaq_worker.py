import logging
from PyQt5.QtCore import QRunnable, pyqtSlot
# from widgets.hardware.alternative_control import NIdaq
from widgets.gui.qt_worker_signals import WorkerSignals

logging.basicConfig(format="%(message)s", level=logging.INFO)


class NIDaqWorker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(NIDaqWorker, self).__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.daq_card = None

    @pyqtSlot()
    def run(self):
        logging.info("NIDaq Instance launched")
        self.signals.launching.emit()
        try:
            self.fn(*self.args, **self.kwargs)

        finally:
            self.signals.finished.emit()
            print("finished emitted")

    def stop(self):
        #self.daq_card.stop_now = True
        print("stop called")
        self.fn.thread_running = False

