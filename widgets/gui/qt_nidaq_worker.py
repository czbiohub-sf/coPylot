from PyQt5.QtCore import QRunnable, pyqtSlot
from widgets.gui.qt_worker_signals import WorkerSignals
from widgets.hardware.alternative_control import NIdaq


class NIDaqWorker(QRunnable):
    def __init__(self, view, channel, parameters, *args, **kwargs):
        super(NIDaqWorker, self).__init__()

        self.view = view
        self.channel = channel
        self.parameters = parameters
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.daq_card = NIdaq(self, **parameters)
        self.thread_running = True

    @pyqtSlot()
    def run(self):
        try:
            self.signals.running.emit()
            # self.fn(self, *self.args, **self.kwargs)
            self.daq_card.select_view(self.view)
            self.daq_card.select_channel_remove_stripes(self.channel)

        finally:
            self.signals.finished.emit()

    def stop(self):
        self.daq_card.stop_now = True
        # self.thread_running = False
