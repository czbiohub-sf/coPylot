from PyQt5.QtWidgets import QWidget, QComboBox, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot

from copylot.gui.qt_nidaq_worker import NIDaqWorker


class TimelapseControl(QWidget):
    trigger_stop_timelapse = pyqtSignal()

    def __init__(self, parent, threadpool):
        super(QWidget, self).__init__(parent)

        self.parent = parent
        self.button_name = "Timelapse Mode"
        self.threadpool = threadpool

        self.state_tracker = (
            False  # tracker to set new background color when timelapse mode is on
        )

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        # button to call nidaq launcher
        self.section_button = QPushButton(self.button_name)
        self.section_button.pressed.connect(self.handle_nidaq_launch)
        self.layout.addWidget(self.section_button)

        # view and channel combobox widgets and options
        self.view_combobox = QComboBox()
        self.view_combobox.addItem("view 1")
        self.view_combobox.addItem("view 2")
        self.view_combobox.addItem("view 1 and 2")
        self.layout.addWidget(self.view_combobox)

        self.laser_combobox = QComboBox()
        self.laser_combobox.addItem("488")
        self.laser_combobox.addItem("561")
        self.laser_combobox.addItem("488 and 561")
        self.layout.addWidget(self.laser_combobox)

        self.setLayout(self.layout)

    def launch_nidaq(self):
        if self.state_tracker:
            self.parent.status_bar.showMessage("Timelapse mode running...")

            # launch worker thread with newest parameters
            daq_card_worker = NIDaqWorker(
                "timelapse",
                self.combobox_view,
                self.combobox_channel,
                self.parent.parameters_widget.parameters,
            )
            print(
                "called with:",
                self.parent.parameters_widget.parameters,
                "view",
                self.combobox_view + 1 if self.combobox_view != 2 else "1 and 2",
                "and channel",
                *self.combobox_channel,
            )

            # connect signals
            self.trigger_stop_timelapse.connect(daq_card_worker.stop)
            daq_card_worker.signals.finished.connect(self.status_finished)

            self.threadpool.start(daq_card_worker)

    def handle_nidaq_launch(self):
        self.state_tracker = not self.state_tracker

        # disable timelapse parameter inputs and live mode
        self.parent.parameters_widget.toggle_button.setDisabled(self.state_tracker)
        self.view_combobox.setDisabled(self.state_tracker)
        self.laser_combobox.setDisabled(self.state_tracker)
        self.parent.live_widget.setDisabled(self.state_tracker)

        # disable parameter inputs
        for parameter_object in self.parent.parameters_widget.parameter_objects:
            parameter_object.spinbox.setDisabled(self.state_tracker)
            parameter_object.slider.setDisabled(self.state_tracker)

        # launch or stop worker & change style sheet depending on current state
        if self.state_tracker:
            self.section_button.setStyleSheet("background-color: red")
            self.launch_nidaq()
        else:
            self.section_button.setStyleSheet("")
            self.trigger_stop_timelapse.emit()

    @property
    def combobox_view(self):
        return self.view_combobox.currentIndex()

    @property
    def combobox_channel(self):
        return (
            [int(self.laser_combobox.currentText())]
            if self.laser_combobox.currentIndex() != 2
            else [488, 561]
        )

    @pyqtSlot()
    def status_finished(self):
        self.parent.status_bar.showMessage("NIDaq idle...")
