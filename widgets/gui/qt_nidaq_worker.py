from PyQt5.QtCore import QRunnable, pyqtSlot
from widgets.gui.qt_worker_signals import WorkerSignals


class NIDaqWorker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(NIDaqWorker, self).__init__()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.daq_card = None
        self.thread_running = True

    @pyqtSlot()
    def run(self):
        try:
            self.signals.running.emit()
            self.fn(self, *self.args, **self.kwargs)

        finally:
            self.signals.finished.emit()

    def stop(self):
        self.daq_card.stop_now = True
        # self.thread_running = False
