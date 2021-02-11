from PyQt5.QtWidgets import QWidget, QApplication, QComboBox, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QRunnable, QThreadPool
import time
import logging
from widgets.gui.qt_nidaq_worker import NIDaqWorker

logging.basicConfig(format="%(message)s", level=logging.INFO)


class LiveControl(QWidget):
    trigger_stop_live = pyqtSignal()

    def __init__(self, parent, button_name):
        super(QWidget, self).__init__(parent)

        self.parent = parent
        self.button_name = button_name

        self.state_tracker = False  # tracks if live mode is on
        self.wait_shutdown = False
        self.nidaq_running = False
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

    def launch_nidaq(self):
        print("state_tracker", self.state_tracker)
        if self.state_tracker:
            self.trigger_stop_live.emit()  # does nothing on first iteration before thread is made.
            # Stops thread before new one is launched. Needed when instanced on parameter change.
            # Not needed in timelapse

            print("back at wait")

            while True:
                time.sleep(0.05)
                if not self.wait_shutdown:
                    break
                QApplication.processEvents()
            self.wait_shutdown = True  # reset to true for next call

            parameters = self.parent.left_window.update_parameters
            view = self.view_combobox.currentText()
            channel = self.laser_combobox.currentText()

            print("called with:", parameters, view, "and channel", channel)

            # launch worker thread with newest parameters
            daq_card_worker = NIDaqWorker(parameters, view, channel)
            # connect
            daq_card_worker.signals.finished.connect(self.update_wait_shutdown)
            self.trigger_stop_live.connect(daq_card_worker.stop)

            self.q_thread_pool.start(daq_card_worker)

            if not self.state_tracker:
                self.trigger_stop_live.emit()

    def button_state_change(self):
        self.state_tracker = not self.state_tracker

        if self.state_tracker:
            self.section_button.setStyleSheet("background-color: red")
            self.launch_nidaq()
        else:
            self.section_button.setStyleSheet("")
            self.trigger_stop_live.emit()
            print("final stop emitted")

    def update_wait_shutdown(self):
        print("update_wait_shutdown called")
        self.wait_shutdown = False
        print("finished signal received")

