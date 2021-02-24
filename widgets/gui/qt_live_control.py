from PyQt5.QtWidgets import QWidget, QApplication, QComboBox, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QRunnable, QThreadPool, pyqtSlot
import time
import logging

from widgets.gui.qt_nidaq_worker import NIDaqWorker
from widgets.hardware.alternative_control import NIdaq

logging.basicConfig(format="%(message)s", level=logging.INFO)


class LiveControl(QWidget):
    trigger_stop_live = pyqtSignal()
    thread_launching = pyqtSignal()

    def __init__(self, parent, button_name):
        super(QWidget, self).__init__(parent)

        self.parent = parent
        self.button_name = button_name

        self.state_tracker = False  # tracks if live mode is on
        self.wait_shutdown = False
        self.daq_card_thread: QRunnable

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        # add instance launching button
        self.section_button = QPushButton(self.button_name)

        self.layout.addWidget(self.section_button)
        self.section_button.pressed.connect(self.button_state_change)

        # placeholders for future selection options
        self.view_combobox = QComboBox()
        self.view_combobox.addItem("view 1")
        self.view_combobox.addItem("view 2")
        self.layout.addWidget(self.view_combobox)
        self.view_combobox.activated.connect(self.launch_nidaq)

        self.laser_combobox = QComboBox()
        self.laser_combobox.addItem("488")
        self.laser_combobox.addItem("561")
        self.layout.addWidget(self.laser_combobox)
        self.laser_combobox.activated.connect(self.launch_nidaq)

        self.setLayout(self.layout)

        self.q_thread_pool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.q_thread_pool.maxThreadCount())

        self.thread_launching.connect(self.status_launching)

    def launch_nidaq(self):
        if self.state_tracker:
            self.thread_launching.emit()
            self.trigger_stop_live.emit()  # does nothing on first iteration before thread is made.
            # Stops thread before new one is launched. Needed when instanced on parameter change.
            # Not needed in timelapse

            while True:
                time.sleep(0.05)
                if not self.wait_shutdown:
                    break
                QApplication.processEvents()
            self.wait_shutdown = True  # reset to true for next call

            daq_card_worker = NIDaqWorker(self.live_worker)

            # connect
            daq_card_worker.signals.running.connect(self.status_running)
            daq_card_worker.signals.finished.connect(self.update_wait_shutdown)
            self.trigger_stop_live.connect(daq_card_worker.stop)

            self.q_thread_pool.start(daq_card_worker)

            # because processEvents runs while waiting for wait_shutdown = False, if pressed quickly, live mode can
            # emit final trigger_stop_live.emit before final worker is initialized, preventing a proper shutdown.
            if not self.state_tracker:
                self.trigger_stop_live.emit()

    def live_worker(self, parent_worker):
        parameters = self.parent.left_window.parameters
        view = self.combobox_view
        channel = self.combobox_channel

        print("called with:", parameters, view, "and channel", channel)

        # while True:
        #     time.sleep(1)
        #     logging.info(parent_worker.thread_running)
        #     if not parent_worker.thread_running:
        #         break

        self.daq_card = NIdaq(self, **parameters)
        self.daq_card.select_view(view)
        self.daq_card.select_channel_remove_stripes(channel)

    def button_state_change(self):
        self.state_tracker = not self.state_tracker

        if self.state_tracker:
            self.section_button.setStyleSheet("background-color: red")
            self.launch_nidaq()
        else:
            self.section_button.setStyleSheet("")
            self.trigger_stop_live.emit()
            self.parent.parent.status_bar.showMessage("NIDaq idle...")

    @pyqtSlot()
    def status_launching(self):
        self.parent.parent.status_bar.showMessage("Live mode launching...")

    @pyqtSlot()
    def status_running(self):
        self.parent.parent.status_bar.showMessage("Live mode running...")

    def update_wait_shutdown(self):
        self.wait_shutdown = False

    @property
    def combobox_view(self):
        return self.view_combobox.currentIndex() + 1

    @property
    def combobox_channel(self):
        return int(self.laser_combobox.currentText())
