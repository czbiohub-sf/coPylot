from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from widgets.gui import qt_nidaq_worker
from widgets.hardware.control import NIDaq


class LiveControl(QWidget):
    trigger_stop_live = pyqtSignal()

    def __init__(self, parent, button_name):
        super(QWidget, self).__init__(parent)

        self.parent = parent
        self.button_name = button_name

        self.state_tracker = False  # tracks if live mode is on
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
        self.view_combobox.activated.connect(self.launch_nidaq_instance)

        self.laser_combobox = QComboBox()
        self.laser_combobox.addItem("488")
        self.laser_combobox.addItem("561")
        self.layout.addWidget(self.laser_combobox)
        self.laser_combobox.activated.connect(self.launch_nidaq_instance)

        self.setLayout(self.layout)

        self.q_thread_pool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.q_thread_pool.maxThreadCount())

    def launch_nidaq_instance(self):
        if self.state_tracker:
            self.trigger_stop_live.emit()  # does nothing on first iteration before thread is made.
            # Stops thread before new one is launched. Needed when instanced on parameter change.
            # Not needed in timelapse

            parameters = self.parent.left_window.update_parameters
            view = self.view_combobox.currentText()
            channel = self.laser_combobox.currentText()

            print("called with:", parameters, view, "and channel",
                  channel)

            # launch worker thread with newest parameters
            daq_card_thread = qt_nidaq_worker.NIDaqWorker(parameters, view, channel)
            self.q_thread_pool.start(daq_card_thread)

            # connect
            self.trigger_stop_live.connect(daq_card_thread.stop)

        else:
            self.trigger_stop_live.emit()  # launch_nidaq_instance is called from button_state_change,
            # so function is called one more time after live mode is turned off,
            # with state_tracker = False, killing final thread

    def button_state_change(self):
        self.state_tracker = not self.state_tracker
        self.launch_nidaq_instance()

        self.parent.toggle_disabled("live")
        if self.state_tracker:
            self.section_button.setStyleSheet("background-color: red")
        else:
            self.section_button.setStyleSheet("")
