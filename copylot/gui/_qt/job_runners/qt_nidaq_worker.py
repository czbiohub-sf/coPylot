from qtpy.QtCore import QRunnable, Slot

from copylot.gui._qt.job_runners.worker import WorkerSignals
from copylot.hardware.ni_daq.nidaq import NIDaq


class NIDaqWorker(QRunnable):
    def __init__(self, program_type, view, channel, parameters, *args, **kwargs):
        super(NIDaqWorker, self).__init__()

        self.program_type = program_type
        self.view = view
        self.channel = channel
        self.parameters = parameters
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.daq_card = NIDaq(self, **parameters)
        self.thread_running = False

    @Slot()
    def run(self):
        try:
            self.signals.running.emit()
            self.thread_running = True
            # self.fn(self, *self.args, **self.kwargs)
            if self.program_type == "live":
                self.daq_card.select_view(self.view)
                self.daq_card.select_channel_remove_stripes(self.channel)
            elif self.program_type == "timelapse":
                self.daq_card.acquire_stacks(channels=self.channel, view=self.view)

        finally:
            self.signals.finished.emit()

    def stop(self):
        self.daq_card.stop_now = True
        self.thread_running = False
