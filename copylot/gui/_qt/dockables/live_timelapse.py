from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton

from copylot.hardware.ni_daq.nidaq import NIDaq


class LiveTimelapseDockWidget(QWidget):
    def __init__(self, parent, threadpool):
        super(QWidget, self).__init__(parent)

        self.parent = parent
        self.threadpool = threadpool

        self.running = False
        self.wait_before_shutdown = False

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        # add instance launching button
        self.section_button = QPushButton("Live/Timelapse Button")

        self.layout.addWidget(self.section_button)

        self.setLayout(self.layout)

    def timelapse_worker_method(self):
        view = self.view_combobox.currentIndex()
        channel = (
            [int(self.laser_combobox.currentText())]
            if self.laser_combobox.currentIndex() != 2
            else [488, 561]
        )
        parameters = self.parent.parameters_widget.parameters

        daq_card = NIDaq(self, **parameters)
        daq_card.acquire_stacks(channels=channel, view=view)

    def live_worker_method(self):
        view = self.combobox_view
        channel = self.combobox_channel
        parameters = self.parent.parameters_widget.parameters

        daq_card = NIDaq(self, **parameters)
        daq_card.select_view(view)
        daq_card.select_channel_remove_stripes(channel)
