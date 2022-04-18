from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton


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
