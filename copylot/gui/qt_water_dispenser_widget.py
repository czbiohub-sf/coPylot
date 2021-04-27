from PyQt5.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QDoubleSpinBox,
    QSpinBox,
    QAbstractSpinBox,
)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QRunnable
from copylot.hardware.water_dispenser import WaterDispenserControl
from copylot.gui.qt_worker_signals import WorkerSignals


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

        self.param_list = [self.interval, self.duration, self.freq, self.amp]
        self.param_names = ["interval", "duration", "freq", "amp"]
        self.defaults = [3, 6, 25, 100]

        grid_counter = 0

        for param in self.param_list:
            param.setValue(self.defaults[grid_counter])
            param.setMaximum(1000)

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
                self.interval_state,
                self.duration_state,
                self.freq_state,
                self.amp_state,
            ]

            water_worker = WaterWorker(self, parameters)
            self.trigger_stop.connect(water_worker.stop)
            self.threadpool.start(water_worker)

        else:
            self.section_button.setText("Run for Recording")
            self.section_button.setStyleSheet("")
            self.state_tracker = False

            self.trigger_stop.emit()

    @property
    def interval_state(self):
        return self.interval.value()

    @property
    def duration_state(self):
        return self.duration.value()

    @property
    def freq_state(self):
        return self.freq.value()

    @property
    def amp_state(self):
        return self.amp.value()


class WaterWorker(QRunnable):
    def __init__(self, parent, parameters):
        super().__init__()
        self.parent = parent
        self.parameters = parameters
        self.water_control = WaterDispenserControl()
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        self.water_control.run_for_recording(*self.parameters)

    def stop(self):
        self.water_control.stop_now = True
