from PyQt5.QtWidgets import QWidget, QApplication, QComboBox, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QRunnable, QThreadPool
import time
import logging

from widgets.gui import qt_line_break
from widgets.gui.qt_nidaq_worker import NIDaqWorker
# from widgets.hardware.control import NIDaq
from widgets.hardware.alternative_control import NIdaq


class TimelapseControl(QWidget):
    trigger_stop_timelapse = pyqtSignal()

    def __init__(self, parent, button_name):
        super(QWidget, self).__init__(parent)

        self.parent = parent
        self.button_name = button_name

        self.state_tracker = False  # tracker to set new background color when timelapse mode is on

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        self.layout.addWidget(qt_line_break.LineBreak(Qt.AlignTop))  # line break between live and timelapse

        # add launch button that disables parameter input, preventing input change
        self.section_button = QPushButton(self.button_name)
        self.section_button.pressed.connect(self.button_state_change)
        self.layout.addWidget(self.section_button)

        # placeholders for future selection options
        self.view_combobox = QComboBox()
        self.view_combobox.addItem("view 1")
        self.view_combobox.addItem("view 2")
        self.layout.addWidget(self.view_combobox)

        self.laser_combobox = QComboBox()
        self.laser_combobox.addItem("488")
        self.laser_combobox.addItem("561")
        self.layout.addWidget(self.laser_combobox)

        self.setLayout(self.layout)

        self.q_thread_pool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.q_thread_pool.maxThreadCount())

    def launch_nidaq_instance(self):
        print("state_tracker", self.state_tracker)
        if self.state_tracker:
            # launch worker thread with newest parameters
            daq_card_worker = NIDaqWorker(self.timelapse_worker)

            # connect
            self.trigger_stop_timelapse.connect(daq_card_worker.stop)

            self.q_thread_pool.start(daq_card_worker)

            # because processEvents runs while waiting for wait_shutdown = False, if pressed quickly, live mode can
            # emit final trigger_stop_live.emit before final worker is initialized, preventing a proper shutdown.

    def timelapse_worker(self, parent_worker):
        parameters = self.parent.left_window.parameters
        view = self.combobox_view
        channel = self.combobox_channel

        print("called with:", parameters, view, "and channel", channel)

        while True:
            time.sleep(1)
            logging.info(parent_worker.thread_running)
            if not parent_worker.thread_running:
                break

        # self.daq_card = NIdaq(self, **parameters)
        # self.daq_card.select_view(view)
        # self.daq_card.select_channel_remove_stripes(channel)

    def button_state_change(self):

        self.state_tracker = not self.state_tracker

        self.parent.toggle_disabled()
        if self.state_tracker:
            self.section_button.setStyleSheet("background-color: red")
            self.launch_nidaq_instance()
        else:
            self.section_button.setStyleSheet("")
            self.trigger_stop_timelapse.emit()

    @property
    def combobox_view(self):
        return self.view_combobox.currentIndex() + 1

    @property
    def combobox_channel(self):
        return int(self.laser_combobox.currentText())
