from PyQt5.QtWidgets import QWidget, QApplication, QComboBox, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
import time

from copylot.gui.qt_nidaq_worker import NIDaqWorker


class LiveControl(QWidget):
    trigger_stop_live = pyqtSignal()
    thread_launching = pyqtSignal()

    def __init__(self, parent, threadpool):
        super(QWidget, self).__init__(parent)

        self.parent = parent
        self.button_name = "Live Mode"
        self.threadpool = threadpool

        self.state_tracker = False  # tracks if live mode is on
        self.wait_shutdown = False

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        # add instance launching button
        self.section_button = QPushButton(self.button_name)

        self.layout.addWidget(self.section_button)
        self.section_button.pressed.connect(self.handle_nidaq_launch)

        # view and channel combobox widgets and options
        self.view_combobox = QComboBox()
        self.view_combobox.addItem("view 1")
        self.view_combobox.addItem("view 2")
        self.view_combobox.setCurrentIndex(self.parent.defaults["live"]["view"])

        self.layout.addWidget(self.view_combobox)
        self.view_combobox.activated.connect(self.launch_nidaq)

        self.laser_combobox = QComboBox()
        self.laser_combobox.addItem("488")
        self.laser_combobox.addItem("561")
        self.laser_combobox.setCurrentIndex(self.parent.defaults["live"]["laser"])

        self.layout.addWidget(self.laser_combobox)
        self.laser_combobox.activated.connect(self.launch_nidaq)

        self.setLayout(self.layout)

        self.thread_launching.connect(self.status_launching)

    def launch_nidaq(self):
        if self.state_tracker:
            self.thread_launching.emit()
            self.trigger_stop_live.emit()  # does nothing on first iteration before thread is made.
            # Stops thread before new one is launched. Needed when instanced on parameter change.

            while True:
                time.sleep(0.05)
                if not self.wait_shutdown:
                    break
                QApplication.processEvents()
            self.wait_shutdown = True  # reset to true for next call

            daq_card_worker = NIDaqWorker(
                "live",
                self.combobox_view,
                self.combobox_channel,
                self.parent.parameters_widget.parameters,
            )

            print(
                "called with:",
                self.parent.parameters_widget.parameters,
                "view",
                self.combobox_view,
                "and channel",
                self.combobox_channel,
            )

            # connect
            daq_card_worker.signals.running.connect(self.status_running)
            daq_card_worker.signals.finished.connect(self.update_wait_shutdown)
            self.trigger_stop_live.connect(daq_card_worker.stop)

            self.threadpool.start(daq_card_worker)

            # because processEvents runs while waiting for wait_shutdown = False, if pressed quickly, live mode can
            # emit final trigger_stop_live.emit before final worker is initialized, preventing a proper shutdown.
            if not self.state_tracker:
                self.trigger_stop_live.emit()

    def handle_nidaq_launch(self):
        self.state_tracker = not self.state_tracker

        self.parent.timelapse_widget.setDisabled(self.state_tracker)

        if self.state_tracker:
            self.section_button.setStyleSheet("background-color: red")
            self.launch_nidaq()
        else:
            self.section_button.setStyleSheet("")
            self.trigger_stop_live.emit()

    def update_wait_shutdown(self):
        self.wait_shutdown = False
        # reset to idle status is here to prevent 'running' displaying if live mode exited while spinbox is selected
        if not self.state_tracker:
            self.parent.status_bar.showMessage("NIDaq idle...")

    @pyqtSlot()
    def status_launching(self):
        self.parent.status_bar.showMessage("Live mode launching...")

    @pyqtSlot()
    def status_running(self):
        self.parent.status_bar.showMessage("Live mode running...")

    @property
    def combobox_view(self):
        return self.view_combobox.currentIndex() + 1

    @property
    def combobox_channel(self):
        return int(self.laser_combobox.currentText())
