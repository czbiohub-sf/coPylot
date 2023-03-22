from qtpy.QtWidgets import (
    QWidget,
    QApplication,
    QComboBox,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QGroupBox,
    QGridLayout,
    QSlider,
    QTabWidget,
    QDesktopWidget,
)
from qtpy.QtCore import Qt, Signal, Slot
import time

from copylot.gui._qt.job_runners.worker import Worker
from copylot.gui._qt.photom_control.tab_manager import TabManager
from copylot.gui._qt.custom_widgets.photom_live_window import LiveViewWindow
# from widgets.utils.affinetransform import AffineTransform
import os
demo_mode = True
print('Running in the UI demo mode. (from ControlPanel)')

class PhotomControlDockWidget(QWidget):
    # TODO: Need to define the threads needed
    # thread_launching = Signal()
    def __init__(self, parent, threadpool):
        super(QWidget, self).__init__(parent)
        self.demo_mode = demo_mode

        num_screens = QDesktopWidget().screenCount()
        # Determine window sizes
        self.liveViewGeo = (
            QDesktopWidget().screenGeometry(num_screens - 1).left(),
            QDesktopWidget().screenGeometry(num_screens - 1).top(),
            min(QDesktopWidget().screenGeometry(num_screens - 1).width() - 400, 1000),
            min(QDesktopWidget().screenGeometry(num_screens - 1).height(), 1000),
        )
        print(f'liveViewGeo {self.liveViewGeo}')
        self.ctrlPanelGeo = (
            QDesktopWidget().screenGeometry(num_screens - 1).left() + self.liveViewGeo[2],
            QDesktopWidget().screenGeometry(num_screens - 1).top(),
            400,
            self.liveViewGeo[3],
        )
        print(f'ctrlPanelGeo {self.ctrlPanelGeo}')
        self.parent = parent
        self.threadpool = threadpool
        self.state_tracker = False
        #===============================================
        #Laser and galco
        self.current_laser = 0

        #=============================================
         # Create folder for saving calibration matrix and other stuff
        self.savepath_configs = 'stored_configs'
        self.savepath_scshot = 'screenshot'
        os.makedirs(self.savepath_configs, exist_ok=True)
        os.makedirs(self.savepath_scshot, exist_ok=True)
        # Get paramters from the DAC board
        self.demo_mode = demo_mode
        self.board_num = 0
        self.ao_range = None

        # Set the main Layout
        self.main_layout = QGridLayout()

        # Photom overlay window
        self.window1 = LiveViewWindow(self)
        self.tabmanager = TabManager(self)
        # Buttons
        self.sl_opacity = QSlider(Qt.Horizontal)
        self.sl_opacity.setRange(0, 100)
        self.sl_opacity.setValue(int(self.window1.opacity * 100))
        self.opacity_indicator = QLabel(f'Opacity {0.0 * 100} %')
        self.sl_opacity.valueChanged.connect(self.change_trancparancy)

        # Set the Widget Layout
        self.layout = QGridLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.addWidget(self.sl_opacity, 0, 0)
        self.layout.addWidget(self.opacity_indicator, 0, 1)

        # Tab Manager
        self.layout.addWidget(self.tabmanager, 3, 0, 1, 3)
        # def handle_photom_launch(self):
        #     self.state_tracker = not self.state_tracker
        #     if self.state_tracker:
        #         self.setStyleSheet("background-color: red;")
        #     else:
        #         scshot_box = QGroupBox('Screen shot')
        #         scshot_box.setStyleSheet('font-size: 14pt')
        #         scshot_box.layout = QGridLayout()
        #         scshot_box.layout.addWidget(self.le_scshot, 0, 0)
        #         scshot_box.layout.addWidget(self.pb_scshot, 0, 1)
        #         scshot_box.setLayout(scshot_box.layout)
        self.setLayout(self.layout)

    @property
    def parameters(self):
        raise NotImplementedError("parameters not yet implemented")

    def change_trancparancy(self):
        self.opacity_indicator.setText(f'Opacity {self.sl_opacity.value()} %')
        self.window1.opacity = self.sl_opacity.value() / 100
        self.window1.setWindowOpacity(self.window1.opacity)


