from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qt_line_break
from widgets.gui import qt_nidaq_worker
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
        if self.state_tracker:

            parameters = self.parent.left_window.update_parameters
            view = self.view_combobox.currentText()
            channel = self.laser_combobox.currentText()

            print("launched with:", parameters, view, "and channel", channel)

            daq_card_thread = qt_nidaq_worker.NIDaqWorker(parameters, view, channel)
            self.q_thread_pool.start(daq_card_thread)

            # connect
            self.trigger_stop_timelapse.connect(daq_card_thread.stop)

        else:
            self.trigger_stop_timelapse.emit()

    def button_state_change(self):

        self.state_tracker = not self.state_tracker
        self.launch_nidaq_instance()

        self.parent.toggle_disabled("timelapse")
        if self.state_tracker:
            self.section_button.setStyleSheet("background-color: red")
        else:
            self.section_button.setStyleSheet("")
