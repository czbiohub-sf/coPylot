from PyQt5.QtWidgets import QWidget, QApplication, QComboBox, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QRunnable, QThreadPool
import time
import logging

from widgets.gui import qt_line_break
from widgets.gui.qt_nidaq_worker import NIDaqWorker
# from widgets.hardware.control import NIDaq


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

            parameters = self.parent.left_window.update_parameters
            view = self.view_combobox.currentText()
            channel = self.laser_combobox.currentText()

            print("called with:", parameters, view, "and channel", channel)

            # launch worker thread with newest parameters
            daq_card_worker = NIDaqWorker(self.timelapse_worker, [parameters, view, channel])

            # connect
            self.trigger_stop_timelapse.connect(daq_card_worker.stop)

            self.q_thread_pool.start(daq_card_worker)

            # because processEvents runs while waiting for wait_shutdown = False, if pressed quickly, live mode can
            # emit final trigger_stop_live.emit before final worker is initialized, preventing a proper shutdown.

    def timelapse_worker(self, parent_worker, args):
        parameters = args[0]
        view = int(args[1][5])
        channel = int(args[2])

        while True:
            time.sleep(1)
            logging.info(parent_worker.thread_running)
            if not parent_worker.thread_running:
                break

        # self.daq_card = NIdaq(self,
        #                      exposure=self.parameters[0],
        #                      nb_timepoints=self.parameters[1],
        #                      scan_step=self.parameters[2],
        #                      stage_scan_range=self.parameters[3],
        #                      vertical_pixels=self.parameters[4],
        #                      num_samples=self.parameters[5],
        #                      offset_view1=self.parameters[6],
        #                      offset_view2=self.parameters[7],
        #                      view1_galvo1=self.parameters[8],
        #                      view1_galvo2=self.parameters[9],
        #                      view2_galvo1=self.parameters[10],
        #                      view2_galvo2=self.parameters[11],
        #                      stripe_reduction_range=self.parameters[12],
        #                      stripe_reduction_offset=self.parameters[13])
        #
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
