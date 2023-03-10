from qtpy.QtWidgets import QWidget, QApplication, QComboBox, QPushButton, QVBoxLayout
from qtpy.QtCore import Qt, Signal, Slot
import time

from copylot.gui._qt.job_runners.worker import Worker
# from widgets.utils.affinetransform import AffineTransform

class PhotomControlDockWidget(QWidget):
    #TODO: Need to define the threads needed
    # thread_launching = Signal()
    # 
    def __init__(self, parent, threadpool):
        super(QWidget, self).__init__(parent)

        self.parent = parent
        self.launch_btn_txt = "Launch Photom"
        self.threadpool = threadpool
        self.state_tracker = False

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        #Add the launching button
        self.section_button = QPushButton(self.launch_btn_txt)
        self.layout.addWidget(self.section_button)
        self.section_button.pressed.connect(self.handle_photom_launch)


    def handle_photom_launch(self):
        self.state_tracker = not self.state_tracker
        if self.state_tracker:
            self.section_button.setStyleSheet("background-color: red")
        else:
            self.section_button.setStyleSheet("")
            self.trigger_stop_live.emit()