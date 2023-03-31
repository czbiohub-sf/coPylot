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
    QMessageBox,
)
from qtpy.QtCore import Qt, Signal, Slot
import time

from copylot.gui._qt.job_runners.worker import Worker
from copylot.gui._qt.photom_control.tab_manager import TabManager
from copylot.gui._qt.custom_widgets.photom_live_window import LiveViewWindow
from copylot.gui._qt.photom_control.utils.affinetransform import AffineTransform
from copylot.gui._qt.photom_control.helper_functions.messagebox import MessageBox
from copylot.gui._qt.custom_widgets.qt_logger import QtLogger, QtLogBox
import os
import logging
from copylot import logger

# This flag disables the loading of the DACs and lasers.
demo_mode = True
dac_mode = False


if not demo_mode:
    from copylot.hardware.lasers.vortran import vortran
    from copylot.hardware.mirrors.optotune import mirror

    serial_num = ''
    laser_port = ''
    mirror_port = ''
    # from copylot.hardware.lasers import

print('Running in the UI demo mode. (from ControlPanel)')


# TODO: setup a filelogger location
class PhotomControlDockWidget(QWidget):
    # TODO: Need to define the threads needed
    # thread_launching = Signal()
    def __init__(self, parent, threadpool):
        super(QWidget, self).__init__(parent)

        # Variables for testing purposes to run demo mode or dac mode
        self.demo_mode = demo_mode
        self.dac_mode = dac_mode
        self.logger = logger
        # Get the number of screens and make the live view
        num_screens = QDesktopWidget().screenCount()
        # Determine window sizes
        self.liveViewGeo = (
            QDesktopWidget().screenGeometry(num_screens - 1).left(),
            QDesktopWidget().screenGeometry(num_screens - 1).top(),
            min(QDesktopWidget().screenGeometry(num_screens - 1).width() - 400, 800),
            min(QDesktopWidget().screenGeometry(num_screens - 1).height(), 800),
        )
        print(f'liveViewGeo {self.liveViewGeo}')
        self.ctrlPanelGeo = (
            QDesktopWidget().screenGeometry(num_screens - 1).left()
            + self.liveViewGeo[2],
            QDesktopWidget().screenGeometry(num_screens - 1).top(),
            400,
            self.liveViewGeo[3],
        )
        print(f'ctrlPanelGeo {self.ctrlPanelGeo}')
        self.parent = parent
        self.threadpool = threadpool
        self.state_tracker = False
        # ===============================================
        # Laser and galvo
        self.current_laser = (
            0  # this variable is used for knowing which laser to calibrate
        )

        # Scan pattern selection
        self.current_scan_shape = 0
        self.current_scan_pattern = 0

        if self.demo_mode:
            self.mirror_0 = 0
        else:
            # Initialize the laser and the galvo
            self.laser_0 = vortran.VortranLaser(
                serial_number=serial_num, port=laser_port
            )
            self.mirror_0 = mirror.OptoMirror(com_port=mirror_port)
            if self.dac_mode:
                pass
            pass

        # =============================================
        # Create folder for saving calibration matrix and other stuff
        self.savepath_configs = 'stored_configs'
        # self.savepath_scshot = 'screenshot'
        os.makedirs(self.savepath_configs, exist_ok=True)
        # os.makedirs(self.savepath_scshot, exist_ok=True)

        # Set the main Layout
        self.main_layout = QGridLayout()

        # Initialize Logger Stream Handler
        log_box = QtLogBox('Logging')
        # Get the StreamHandler attached to the logger
        log_box_handler = QtLogger(log_box)
        log_box_handler.setFormatter(logging.Formatter("%(levelname)s - %(module)s - %(message)s"))
        log_box_handler.setLevel(logging.DEBUG)
        logger.addHandler(log_box_handler)
        logger.debug(logger.name)
        logger.info(logger.handlers)

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
        self.layout.addWidget(self.tabmanager, 1, 0, 1, 2)
        self.setLayout(self.layout)
        # Logger Panel
        self.layout.addWidget(log_box, 2, 0, 1, 2)
        # ===============================
        # Transform matrix that aligns cursor with laser point
        self.transform_list = [AffineTransform(), AffineTransform()]

    @property
    def parameters(self):
        raise NotImplementedError("parameters not yet implemented")

    def change_trancparancy(self):
        self.opacity_indicator.setText(f'Opacity {self.sl_opacity.value()} %')
        self.window1.opacity = self.sl_opacity.value() / 100
        self.window1.setWindowOpacity(self.window1.opacity)
