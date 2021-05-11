import sys
import glob
import serial
from PyQt5.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QDoubleSpinBox,
    QSpinBox,
    QAbstractSpinBox,
    QComboBox,
)

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QRunnable
from copylot.hardware.water_dispenser_control import WaterDispenserControl
from copylot.gui.qt_worker_signals import WorkerSignals


# provide list of available serial ports
def serial_ports():
    if sys.platform.startswith("win"):
        ports = ["COM%s" % (i + 1) for i in range(256)]
    elif sys.platform.startswith("linux") or sys.platform.startswith("cygwin"):
        ports = glob.glob("/dev/tty[A-Za-z]*")
    elif sys.platform.startswith("darwin"):
        ports = glob.glob("/dev/tty.*")
    else:
        raise EnvironmentError("Unsupported platform")

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


class WaterDispenser(QWidget):
    trigger_stop = pyqtSignal()

    def __init__(self, parent, threadpool):
        super(QWidget, self).__init__(parent)

        self.parent = parent
        self.threadpool = threadpool
        self.button_name = "Run for Recording"

        self.state_tracker = False

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        self.parameter_layout = QGridLayout()
        self.parameter_layout.setAlignment(Qt.AlignTop)

        # add instance launching button
        self.section_button = QPushButton(self.button_name)
        self.section_button.pressed.connect(self.worker_handler)

        # add parameter inputs for run_for_recording
        self.interval = QDoubleSpinBox()
        self.duration = QDoubleSpinBox()
        self.freq = QSpinBox()
        self.amp = QSpinBox()

        self.com = QComboBox()
        self.baudrate = QComboBox()

        self.com.addItems(serial_ports())
        self.baudrate.addItems(map(str, serial.Serial.BAUDRATES))

        self.param_list = [
            self.interval,
            self.duration,
            self.freq,
            self.amp,
            self.com,
            self.baudrate,
        ]
        self.param_names = [
            "interval",
            "duration",
            "freq",
            "amp",
            "serial port",
            "baudrate",
        ]
        grid_counter = 0
        for param in self.param_list:
            if type(param) == QComboBox:
                param.setCurrentIndex(
                    self.parent.defaults["water"][self.param_names[grid_counter]]
                )
            else:
                param.setMaximum(1000)
                param.setValue(
                    self.parent.defaults["water"][self.param_names[grid_counter]]
                )

                if param == QDoubleSpinBox:
                    param.setStepType(QAbstractSpinBox.AdaptiveDecimalStepType)
                    param.setDecimals(3)

            self.parameter_layout.addWidget(
                QLabel(self.param_names[grid_counter]), grid_counter, 0
            )
            self.parameter_layout.addWidget(param, grid_counter, 1)
            grid_counter += 1

        self.layout.addWidget(self.section_button)
        self.layout.addLayout(self.parameter_layout)

        self.setLayout(self.layout)

    @pyqtSlot()
    def worker_handler(self):
        if not self.state_tracker:
            self.section_button.setText("Stop Water")
            self.section_button.setStyleSheet("background-color: red")
            self.state_tracker = True

            parameters = [
                self.interval.value(),
                self.duration.value(),
                self.freq.value(),
                self.amp.value(),
            ]
            serial_parameters = [
                self.com.currentText(),
                int(self.baudrate.currentText()),
            ]

            water_worker = WaterWorker(self, parameters, serial_parameters)
            self.trigger_stop.connect(water_worker.stop)
            self.threadpool.start(water_worker)

        else:
            self.section_button.setText("Run for Recording")
            self.section_button.setStyleSheet("")
            self.state_tracker = False

            self.trigger_stop.emit()


class WaterWorker(QRunnable):
    def __init__(self, parent, parameters, serial_parameters):
        super().__init__()
        self.parent = parent
        self.parameters = parameters
        self.water_control = WaterDispenserControl(*serial_parameters)
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        self.water_control.run_for_recording(*self.parameters)

    def stop(self):
        self.water_control.stop_now = True
