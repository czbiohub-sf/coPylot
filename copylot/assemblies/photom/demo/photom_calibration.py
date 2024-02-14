import sys
from tokenize import Double
from matplotlib.pylab import f
import yaml
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QLabel,
    QSlider,
    QVBoxLayout,
    QGraphicsView,
    QGroupBox,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsItem,
    QGraphicsEllipseItem,
    QStackedWidget,
    QComboBox,
    QFileDialog,
    QLineEdit,
    QGridLayout,
    QProgressBar,
)
from PyQt5.QtGui import QColor, QPen, QFont, QFontMetricsF, QMouseEvent
from copylot.assemblies.photom.utils.scanning_algorithms import (
    calculate_rectangle_corners,
)
from copylot.assemblies.photom.utils.qt_utils import DoubleSlider
import numpy as np
from copylot.assemblies.photom.photom import PhotomAssembly
from typing import Any, Tuple
import time

# DEMO_MODE = True
DEMO_MODE = False

# TODO fix the right click releaser
# TODO: deal with the logic when clicking calibrate. Mirror dropdown
# TODO: update the mock laser and mirror
# TODO: replace the entry boxes tos et the laser powers


class LaserWidget(QWidget):
    def __init__(self, laser):
        super().__init__()
        self.laser = laser

        self.emission_state = 0  # 0 = off, 1 = on
        self.emission_delay = 0  # 0 =off ,1= 5 sec delay

        self._curr_power = 0
        self._slider_decimal = 1
        self._curr_laser_pulse_mode = False

        self.initializer_laser()
        self.initialize_UI()

    def initializer_laser(self):
        # Set the power to 0
        self.laser.toggle_emission = 0
        self.laser.emission_delay = self.emission_delay
        self.laser.pulse_power = self._curr_power
        self.laser.power = self._curr_power

        # Make sure laser is in continuous mode
        if self.laser.pulse_mode == 1:
            self.laser.toggle_emission = 1
            time.sleep(0.2)
            self.laser.pulse_mode = self._curr_laser_pulse_mode ^ 1
            time.sleep(0.2)
            self.laser.toggle_emission = 0

    def initialize_UI(self):
        layout = QVBoxLayout()

        self.laser_label = QLabel(self.laser.name)
        layout.addWidget(self.laser_label)

        self.laser_power_slider = DoubleSlider(
            orientation=Qt.Horizontal, decimals=self._slider_decimal
        )
        self.laser_power_slider.setMinimum(0)
        self.laser_power_slider.setMaximum(100)
        self.laser_power_slider.setValue(self.laser.power)
        self.laser_power_slider.valueChanged.connect(self.update_power)
        layout.addWidget(self.laser_power_slider)

        # Add a QLabel to display the power value
        self.power_edit = QLineEdit(f"{self._curr_power:.2f}")  # Changed to QLineEdit
        self.power_edit.returnPressed.connect(
            self.edit_power
        )  # Connect the returnPressed signal
        layout.addWidget(self.power_edit)

        # Set Pulse Mode Button
        self.pulse_mode_button = QPushButton("Pulse Mode")
        self.pulse_mode_button.clicked.connect(self.laser_pulse_mode)
        layout.addWidget(self.pulse_mode_button)
        self.pulse_mode_button.setStyleSheet("background-color: magenta")

        self.laser_toggle_button = QPushButton("Toggle")
        self.laser_toggle_button.clicked.connect(self.toggle_laser)
        # make it background red if laser is off
        if self.emission_state == 0:
            self.laser_toggle_button.setStyleSheet("background-color: magenta")
        layout.addWidget(self.laser_toggle_button)

        self.setLayout(layout)

    def toggle_laser(self):
        self.emission_state = self.emission_state ^ 1
        self.laser.toggle_emission = self.emission_state
        if self.emission_state == 0:
            self.laser_toggle_button.setStyleSheet("background-color: magenta")
        else:
            self.laser_toggle_button.setStyleSheet("background-color: green")

    def update_power(self, value):
        self._curr_power = value / (10**self._slider_decimal)
        if self._curr_laser_pulse_mode:
            self.laser.pulse_power = self._curr_power
        else:
            self.laser.power = self._curr_power

        # Update the QLabel with the new power value
        self.power_edit.setText(f"{self._curr_power:.2f}")

    def edit_power(self):
        try:
            # Extract the numerical value from the QLineEdit text
            power_value_str = self.power_edit.text()
            power_value = float(power_value_str)

            if (
                0 <= power_value <= 100
            ):  # Assuming the power range is 0 to 100 percentages
                self._curr_power = power_value
                self.laser.power = self._curr_power
                self.laser_power_slider.setValue(self._curr_power)
                self.power_edit.setText(f"{self._curr_power:.2f}")
            else:
                self.power_edit.setText(f"{self._curr_power:.2f}")
            print(f"Power: {self._curr_power}")
        except ValueError:
            self.power_edit.setText(f"{self._curr_power:.2f}")

    def laser_pulse_mode(self):
        self._curr_laser_pulse_mode = not self._curr_laser_pulse_mode
        self.laser.toggle_emission = 1
        if self._curr_laser_pulse_mode:
            self.pulse_mode_button.setStyleSheet("background-color: green")
            self.laser.pulse_power = self._curr_power
            self.laser.pulse_mode = 1
            time.sleep(0.2)
        else:
            self.laser.power = self._curr_power
            self.laser.pulse_mode = 0
            self.pulse_mode_button.setStyleSheet("background-color: magenta")
            time.sleep(0.2)
            self.laser_toggle_button.setStyleSheet("background-color: magenta")
            self.laser.toggle_emission = 0
            self.emission_state = 0

        print(f'pulse mode bool: {self._curr_laser_pulse_mode}')
        print(f'digital modulation = {self.laser.pulse_mode}')


# TODO: connect widget to actual abstract mirror calls
class MirrorWidget(QWidget):
    def __init__(self, mirror):
        super().__init__()
        self.mirror = mirror

        self.check_mirror_limits()
        self.initialize_UI()

    def initialize_UI(self):
        layout = QVBoxLayout()

        mirror_x_label = QLabel("Mirror X Position")
        layout.addWidget(mirror_x_label)

        self.mirror_x_slider = DoubleSlider(orientation=Qt.Horizontal)
        self.mirror_x_slider.setMinimum(self.movement_limits_x[0])
        self.mirror_x_slider.setMaximum(self.movement_limits_x[1])
        self.mirror_x_slider.doubleValueChanged.connect(self.update_mirror_x)
        layout.addWidget(self.mirror_x_slider)

        # Add a QLabel to display the mirror X value
        self.mirror_x_label = QLabel(f"X: {self.mirror.position_x}")
        layout.addWidget(self.mirror_x_label)

        mirror_y_label = QLabel("Mirror Y Position")
        layout.addWidget(mirror_y_label)

        self.mirror_y_slider = DoubleSlider(orientation=Qt.Horizontal)
        self.mirror_y_slider.setMinimum(self.movement_limits_y[0])
        self.mirror_y_slider.setMaximum(self.movement_limits_y[1])
        self.mirror_y_slider.doubleValueChanged.connect(self.update_mirror_y)
        layout.addWidget(self.mirror_y_slider)

        # Add a QLabel to display the mirror Y value
        self.mirror_y_label = QLabel(f"Y: {self.mirror.position_y}")
        layout.addWidget(self.mirror_y_label)

        self.setLayout(layout)

    def update_mirror_x(self, value):
        self.mirror.position_x = value
        # Update the QLabel with the new X value
        self.mirror_x_label.setText(f"X: {value}")

    def update_mirror_y(self, value):
        self.mirror.position_y = value
        # Update the QLabel with the new Y value
        self.mirror_y_label.setText(f"Y: {value}")

    def check_mirror_limits(self):
        movement_limits = self.mirror.movement_limits
        self.movement_limits_x = movement_limits[0:2]
        self.movement_limits_y = movement_limits[2:4]


class ArduinoPWMWidget(QWidget):
    def __init__(self, photom_assembly, arduino_pwm):
        super().__init__()
        self.arduino_pwm = arduino_pwm
        self.photom_assembly = photom_assembly
        # default values
        self.duty_cycle = 50  # [%] (0-100)
        self.time_period_ms = 10  # [ms]
        self.frequency = 1000.0 / self.time_period_ms  # [Hz]
        self.duration = 5000  # [ms]
        self.repetitions = 1  # By default it runs once
        self.time_interval_s = 0  # [s]

        self.command = f"U,{self.duty_cycle},{self.frequency},{self.duration}"

        self.initialize_UI()

    def initialize_UI(self):
        layout = QGridLayout()  # Use QGridLayout

        # Laser Dropdown Menu
        self.laser_dropdown = QComboBox()
        for laser in self.photom_assembly.laser:
            self.laser_dropdown.addItem(laser.name)
        layout.addWidget(QLabel("Select Laser:"), 0, 0)
        layout.addWidget(self.laser_dropdown, 0, 1)
        self.laser_dropdown.currentIndexChanged.connect(self.current_laser_changed)

        # Duty Cycle
        layout.addWidget(QLabel("Duty Cycle [%]:"), 1, 0)
        self.duty_cycle_edit = QLineEdit(f"{self.duty_cycle}")
        self.duty_cycle_edit.returnPressed.connect(self.edit_duty_cycle)
        layout.addWidget(self.duty_cycle_edit, 1, 1)

        # Time Period
        layout.addWidget(QLabel("Time Period [ms]:"), 2, 0)
        self.time_period_edit = QLineEdit(f"{self.time_period_ms}")
        self.time_period_edit.returnPressed.connect(self.edit_time_period)
        layout.addWidget(self.time_period_edit, 2, 1)

        # Duration
        layout.addWidget(QLabel("Duration [ms]:"), 3, 0)
        self.duration_edit = QLineEdit(f"{self.duration}")
        self.duration_edit.returnPressed.connect(self.edit_duration)
        layout.addWidget(self.duration_edit, 3, 1)

        # Repetitions
        layout.addWidget(QLabel("Repetitions:"), 4, 0)
        self.repetitions_edit = QLineEdit(f"{self.repetitions}")
        self.repetitions_edit.textChanged.connect(self.edit_repetitions)
        layout.addWidget(self.repetitions_edit, 4, 1)

        # Time interval
        layout.addWidget(QLabel("Time interval [s]:"), 5, 0)
        self.time_interval_edit = QLineEdit(f"{self.time_interval_s}")
        self.time_interval_edit.textChanged.connect(self.edit_time_interval)
        layout.addWidget(self.time_interval_edit, 5, 1)

        # Apply Button
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.apply_settings)
        layout.addWidget(self.apply_button, 6, 0, 1, 2)

        # Start Button
        self.start_button = QPushButton("Start PWM")
        self.start_button.clicked.connect(self.start_pwm)
        layout.addWidget(self.start_button, 7, 0, 1, 2)

        # Add Stop Button
        self.stop_button = QPushButton("Stop PWM")
        self.stop_button.clicked.connect(self.stop_pwm)
        layout.addWidget(self.stop_button, 8, 0, 1, 2)  # Adjust position as needed

        # Add Progress Bar
        self.progressBar = QProgressBar(self)
        self.progressBar.setMaximum(100)  # Set the maximum value
        layout.addWidget(self.progressBar, 9, 0, 1, 2)  # Adjust position as needed

        self.setLayout(layout)

    def edit_duty_cycle(self):
        try:
            value = float(self.duty_cycle_edit.text())
            self.duty_cycle = value
            self.update_command()
        except ValueError:
            self.duty_cycle_edit.setText(f"{self.duty_cycle}")

    def edit_time_period(self):
        try:
            value = float(self.time_period_edit.text())
            self.time_period_ms = value
            self.frequency = 1000.0 / self.time_period_ms
            self.update_command()
        except ValueError:
            self.time_period_edit.setText(f"{self.time_period}")

    def edit_duration(self):
        try:
            value = float(self.duration_edit.text())
            self.duration = value
            self.update_command()
        except ValueError:
            self.duration_edit.setText(f"{self.duration}")

    def edit_repetitions(self):
        try:
            value = int(self.repetitions_edit.text())
            self.repetitions = value
        except ValueError:
            self.repetitions_edit.setText(
                f"{self.repetitions}"
            )  # Reset to last valid value

    def edit_time_interval(self):
        try:
            value = float(self.time_interval_edit.text())
            self.time_interval_s = value
        except ValueError:
            self.time_interval_edit.setText(
                f"{self.time_interval_s}"
            )  # Reset to last valid value

    def update_command(self):
        self.command = f"U,{self.duty_cycle},{self.frequency},{self.duration}"
        print(f"arduino out: {self.command}")
        self.arduino_pwm.send_command(self.command)

    def start_pwm(self):
        print("Starting PWM...")
        self.pwm_worker = PWMWorker(
            self.arduino_pwm, 'S', self.repetitions, self.time_interval_s, self.duration
        )
        self.pwm_worker.finished.connect(self.on_pwm_finished)
        self.pwm_worker.progress.connect(self.update_progress_bar)
        self.pwm_worker.start()

    def update_progress_bar(self, value):
        self.progressBar.setValue(value)  # Update the progress bar with the new value

    def stop_pwm(self):
        if hasattr(self, 'pwm_worker') and self.pwm_worker.isRunning():
            self.pwm_worker.request_stop()

    def on_pwm_finished(self):
        print("PWM operation completed.")
        # self.progressBar.setValue(0)  # Reset the progress bar

    def current_laser_changed(self, index):
        self._curr_laser_idx = index
        self.apply_settings()

    def apply_settings(self):
        # Implement functionality to apply settings to the selected laser
        self._curr_laser_idx = self.laser_dropdown.currentIndex()
        # TODO: Need to modify the data struct for command for multiple lasers
        if hasattr(self, 'command'):
            self.arduino_pwm.send_command(self.command)


class PhotomApp(QMainWindow):
    def __init__(
        self,
        photom_assembly: PhotomAssembly,
        photom_window_size: Tuple[int, int] = (400, 500),
        photom_window_pos: Tuple[int, int] = (100, 100),
        demo_window=None,
        arduino=[],
    ):
        super().__init__()
        # TODO:temporary for arduino. remove when we replace with dac
        self.arduino_pwm = arduino

        self.photom_window = None
        self.photom_controls_window = None

        self.photom_assembly = photom_assembly
        self.lasers = self.photom_assembly.laser
        self.mirrors = self.photom_assembly.mirror
        self.photom_window_size = photom_window_size
        self.photom_window_pos = photom_window_pos
        self._current_mirror_idx = 0
        self._laser_window_transparency = 0.7

        self.calibration_thread = CalibrationThread(
            self.photom_assembly, self._current_mirror_idx
        )

        if DEMO_MODE:
            self.demo_window = demo_window

        self.initialize_UI()
        self.initializer_laser_marker_window()

    def initializer_laser_marker_window(self):
        # Making the photom_window a square and display right besides the control UI
        window_pos = (
            self.photom_window_size[0] + self.photom_window_pos[0],
            self.photom_window_pos[1],
        )
        window_size = (self.photom_window_size[0], self.photom_window_size[1])
        self.photom_window = LaserMarkerWindow(
            photom_controls=self,
            name='Laser Marker',
            window_size=window_size,
            window_pos=window_pos,
        )

    def initialize_UI(self):
        """
        Initialize the UI.

        """
        self.setGeometry(
            self.photom_window_pos[0],
            self.photom_window_pos[1],
            self.photom_window_size[0],
            self.photom_window_size[1],
        )
        self.setWindowTitle("Laser and Mirror Control App")

        # Adding slider to adjust transparency
        transparency_group = QGroupBox("Photom Transparency")
        transparency_layout = QVBoxLayout()
        # Create a slider to adjust the transparency
        self.transparency_slider = QSlider(Qt.Horizontal)
        self.transparency_slider.setMinimum(0)
        self.transparency_slider.setMaximum(100)
        self.transparency_slider.setValue(
            int(self._laser_window_transparency * 100)
        )  # Initial value is fully opaque
        self.transparency_slider.valueChanged.connect(self.update_transparency)
        transparency_layout.addWidget(self.transparency_slider)

        # Add a QLabel to display the current percent transparency value
        self.transparency_label = QLabel(f"Transparency: 100%")
        transparency_layout.addWidget(self.transparency_label)
        transparency_group.setLayout(transparency_layout)

        # Adding a group box for the lasers
        laser_group = QGroupBox("Lasers")
        laser_layout = QVBoxLayout()
        self.laser_widgets = []
        for laser in self.lasers:
            laser_widget = LaserWidget(laser)
            self.laser_widgets.append(laser_widget)
            laser_layout.addWidget(laser_widget)
        laser_group.setLayout(laser_layout)

        # Adding a group box for the mirror
        mirror_group = QGroupBox("Mirror")
        mirror_layout = QVBoxLayout()

        self.mirror_widgets = []
        for idx, mirror in enumerate(self.mirrors):
            mirror_widget = MirrorWidget(mirror)
            self.mirror_widgets.append(mirror_widget)
            mirror_layout.addWidget(mirror_widget)
        mirror_group.setLayout(mirror_layout)

        # TODO remove if arduino is removed
        # Adding group for arduino PWM
        arduino_group = QGroupBox("Arduino PWM")
        arduino_layout = QVBoxLayout()
        self.arduino_pwm_widgets = []
        for arduino in self.arduino_pwm:
            arduino_pwm_widget = ArduinoPWMWidget(self.photom_assembly, arduino)
            self.arduino_pwm_widgets.append(arduino_pwm_widget)
            arduino_layout.addWidget(arduino_pwm_widget)
        arduino_group.setLayout(arduino_layout)

        # Add the laser and mirror group boxes to the main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(transparency_group)
        main_layout.addWidget(laser_group)
        main_layout.addWidget(mirror_group)
        main_layout.addWidget(arduino_group)  # TODO remove if arduino is removed

        self.mirror_dropdown = QComboBox()
        self.mirror_dropdown.addItems([mirror.name for mirror in self.mirrors])
        main_layout.addWidget(self.mirror_dropdown)
        self.mirror_dropdown.setCurrentIndex(self._current_mirror_idx)
        self.mirror_dropdown.currentIndexChanged.connect(self.mirror_dropdown_changed)

        self.recenter_marker_button = QPushButton("Recenter Marker")
        self.recenter_marker_button.clicked.connect(self.recenter_marker)
        main_layout.addWidget(self.recenter_marker_button)

        self.calibrate_button = QPushButton("Calibrate")
        self.calibrate_button.clicked.connect(self.calibrate)
        main_layout.addWidget(self.calibrate_button)

        self.load_calibration_button = QPushButton("Load Calibration")
        self.load_calibration_button.clicked.connect(self.load_calibration)
        main_layout.addWidget(self.load_calibration_button)

        # Add a "Done Calibration" button (initially hidden)
        self.done_calibration_button = QPushButton("Done Calibration")
        self.done_calibration_button.clicked.connect(self.done_calibration)
        self.done_calibration_button.hide()
        main_layout.addWidget(self.done_calibration_button)

        # Add a "Cancel Calibration" button (initially hidden)
        self.cancel_calibration_button = QPushButton("Cancel Calibration")
        self.cancel_calibration_button.clicked.connect(self.cancel_calibration)
        self.cancel_calibration_button.hide()
        main_layout.addWidget(self.cancel_calibration_button)
        main_widget = QWidget(self)
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)
        self.show()

    def mirror_dropdown_changed(self, index):
        print(f"Mirror dropdown changed to index {index}")
        self._current_mirror_idx = index

        # Reset to (0,0) position
        self.photom_assembly.mirror[self._current_mirror_idx].position = [0, 0]

    def recenter_marker(self):
        self.photom_window.display_marker_center(
            self.photom_window.marker,
            (self.photom_window.canvas_width / 2, self.photom_window.canvas_height / 2),
        )

    def calibrate(self):
        # Implement your calibration function here
        print("Calibrating...")
        # Hide the calibrate button
        self.calibrate_button.hide()
        self.load_calibration_button.hide()
        # Show the "Cancel Calibration" button
        self.cancel_calibration_button.show()
        # Display the rectangle
        self.display_rectangle()
        # Show the "Done Calibration" button
        self.done_calibration_button.show()
        # Get the mirror idx
        selected_mirror_name = self.mirror_dropdown.currentText()
        self._current_mirror_idx = next(
            i
            for i, mirror in enumerate(self.mirrors)
            if mirror.name == selected_mirror_name
        )
        if DEMO_MODE:
            print(f'Calibrating mirror: {self._current_mirror_idx}')
        else:
            self.photom_assembly._calibrating = True
            self.calibration_thread.start()
            self.photom_assembly.mirror[
                self._current_mirror_idx
            ].affine_transform_obj.reset_T_affine()

    def load_calibration(self):
        self.photom_assembly._calibrating = False
        print("Loading calibration...")
        # Prompt the user to select a file
        typed_filename, _ = QFileDialog.getOpenFileName(
            self, "Open Calibration File", "", "YAML Files (*.yml)"
        )
        if typed_filename:
            assert typed_filename.endswith(".yml")
            print("Selected file:", typed_filename)
            # Load the matrix
            self.photom_assembly.mirror[
                self._current_mirror_idx
            ].affine_transform_obj.load_matrix(config_file=typed_filename)
            print(
                f'Loaded matrix:{self.photom_assembly.mirror[self._current_mirror_idx].affine_transform_obj.T_affine}'
            )
            self.photom_window.switch_to_shooting_scene()
            self.photom_window.marker.show()

    def cancel_calibration(self):
        self.photom_assembly._calibrating = False

        # Implement your cancel calibration function here
        print("Canceling calibration...")
        # Hide the "Done Calibration" button
        self.done_calibration_button.hide()
        # Show the "Calibrate" button
        self.calibrate_button.show()
        self.load_calibration_button.show()
        # Show the "X" marker in photom_window
        self.photom_window.marker.show()

        self.cancel_calibration_button.hide()
        # Switch back to the shooting scene
        self.photom_window.switch_to_shooting_scene()

    def done_calibration(self):
        self.photom_assembly._calibrating = False
        # TODO: Logic to return to some position

        ## Perform any necessary actions after calibration is done
        # Get the mirror (target) positions
        self.target_pts = self.photom_window.get_coordinates()

        # Mirror calibration size
        mirror_calib_size = self.photom_assembly._calibration_rectangle_boundaries
        origin = np.array(
            [[pt.x(), pt.y()] for pt in self.target_pts],
            dtype=np.float32,
        )
        # TODO make the dest points from the mirror calibration size
        mirror_x = mirror_calib_size[0] / 2
        mirror_y = mirror_calib_size[1] / 2
        dest = np.array(
            [
                [-mirror_x, -mirror_y],
                [mirror_x, -mirror_y],
                [mirror_x, mirror_y],
                [-mirror_x, mirror_y],
            ]
        )
        T_affine = self.photom_assembly.mirror[
            self._current_mirror_idx
        ].affine_transform_obj.get_affine_matrix(origin, dest)
        print(f"Affine matrix: {T_affine}")

        # Save the affine matrix to a file
        typed_filename, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "YAML Files (*.yml)"
        )
        if typed_filename:
            if not typed_filename.endswith(".yml"):
                typed_filename += ".yml"
            print("Selected file:", typed_filename)
            # Save the matrix
            self.photom_assembly.mirror[
                self._current_mirror_idx
            ].affine_transform_obj.save_matrix(
                matrix=T_affine, config_file=typed_filename
            )
            self.photom_window.switch_to_shooting_scene()
            self.photom_window.marker.show()

            # Hide the "Done Calibration" button
            self.done_calibration_button.hide()
            self.calibrate_button.show()
            self.cancel_calibration_button.hide()

            if DEMO_MODE:
                print(f'origin: {origin}')
                print(f'dest: {dest}')
                # transformed_coords = self.affine_trans_obj.apply_affine(dest)
                transformed_coords = self.photom_assembly.mirror[
                    self._current_mirror_idx
                ].affine_transform_obj.apply_affine(dest)
                print(transformed_coords)
                coords_list = self.photom_assembly.mirror[
                    self._current_mirror_idx
                ].affine_transform_obj.trans_pointwise(transformed_coords)
                print(coords_list)
                self.demo_window.updateVertices(coords_list)
                return
        else:
            print("No file selected")
            # Show dialog box saying no file selected
        print("Calibration done")

    def update_transparency(self, value):
        transparency_percent = value
        self.transparency_label.setText(f"Transparency: {transparency_percent}%")
        opacity = 1.0 - (transparency_percent / 100.0)  # Calculate opacity (0.0 to 1.0)
        self.photom_window.setWindowOpacity(opacity)  # Update photom_window opacity

    def display_rectangle(self):
        self.photom_window.switch_to_calibration_scene()


class PWMWorker(QThread):
    finished = pyqtSignal()
    progress = pyqtSignal(int)  # Signal to report progress
    _stop_requested = False

    def request_stop(self):
        self._stop_requested = True

    def __init__(self, arduino_pwm, command, repetitions, time_interval_s, duration):
        super().__init__()
        self.arduino_pwm = arduino_pwm
        self.command = command
        self.repetitions = repetitions
        self.time_interval_s = time_interval_s
        self.duration = duration

    def run(self):
        # Simulate sending the command and waiting (replace with actual logic)
        for i in range(self.repetitions):
            if self._stop_requested:
                break
            self.arduino_pwm.send_command(self.command)
            # TODO: replace when using a better microcontroller since we dont get signals back rn
            time.sleep(self.duration / 1000)
            self.progress.emit(int((i + 1) / self.repetitions * 100))
            time.sleep(self.time_interval_s)  # Simulate time interval

        self.finished.emit()


class CalibrationThread(QThread):
    finished = pyqtSignal()

    def __init__(self, photom_assembly, current_mirror_idx):
        super().__init__()
        self.photom_assembly = photom_assembly
        self.current_mirror_idx = current_mirror_idx

    def run(self):
        self.photom_assembly.calibrate(
            self.current_mirror_idx,
            rectangle_size_xy=self.photom_assembly._calibration_rectangle_size_xy,
            center=[0.000, 0.000],
        )
        self.finished.emit()


class LaserMarkerWindow(QMainWindow):
    def __init__(
        self,
        photom_controls: QMainWindow = None,
        name="Laser Marker",
        window_size: Tuple = (400, 500),
        window_pos: Tuple = (100, 100),
    ):
        super().__init__()
        self.photom_controls = photom_controls
        self.window_name = name
        self.window_geometry = window_pos + window_size
        self.setMouseTracking(True)
        self.setWindowOpacity(self.photom_controls._laser_window_transparency)

        # Create a QStackedWidget
        # TODO: do we need the stacked widget?
        self.stacked_widget = QStackedWidget()
        # Set the QStackedWidget as the central widget
        self.initialize_UI()
        self.initMarker()

        tetragon_coords = calculate_rectangle_corners(
            [self.canvas_width / 5, self.canvas_height / 5],
            center=[self.canvas_width / 2, self.canvas_height / 2],
        )
        self.init_tetragon(tetragon_coords=tetragon_coords)

        self.setCentralWidget(self.stacked_widget)

        self.switch_to_shooting_scene()

        # Flags for mouse tracking
        # NOTE: these are variables inherited from the photom_controls
        self.calibration_mode = self.photom_controls.photom_assembly._calibrating

        # show the window
        self.show()

        # FLAGS
        self._right_click_hold = False
        self._left_click_hold = False

    def initialize_UI(self):
        print(f'window geometry: {self.window_geometry}')
        self.setWindowTitle(self.window_name)

        # Fix the size of the window
        self.setFixedSize(
            self.window_geometry[2],
            self.window_geometry[3],
        )
        self.sidebar_size = self.frameGeometry().width() - self.window_geometry[2]
        self.topbar_size = self.frameGeometry().height() - self.window_geometry[3]
        self.canvas_width = self.frameGeometry().width() - self.sidebar_size
        self.canvas_height = self.frameGeometry().height() - self.topbar_size

        print(f'sidebar size: {self.sidebar_size}, topbar size: {self.topbar_size}')
        print(f'canvas width: {self.canvas_width}, canvas height: {self.canvas_height}')

    def initMarker(self):
        # Generate the shooting scene
        self.shooting_scene = QGraphicsScene(self)
        self.shooting_scene.setSceneRect(0, 0, self.canvas_width, self.canvas_height)

        # Generate the shooting view
        self.shooting_view = QGraphicsView(self.shooting_scene)
        self.shooting_view.setMouseTracking(True)
        self.setCentralWidget(self.shooting_view)
        self.shooting_view.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # Mouse tracking
        self.shooting_view.installEventFilter(self)
        self.setMouseTracking(True)
        self.marker = QGraphicsSimpleTextItem("X")
        self.marker.setBrush(QColor(255, 0, 0))
        self.marker.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.shooting_view.viewport().installEventFilter(self)
        # Position the marker
        self.display_marker_center(
            self.marker, (self.canvas_width / 2, self.canvas_height / 2)
        )

        self.shooting_scene.addItem(self.marker)
        # Add the view to the QStackedWidget
        self.stacked_widget.addWidget(self.shooting_view)

        # Disable scrollbars
        self.shooting_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.shooting_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def init_tetragon(
        self, tetragon_coords: list = [(100, 100), (200, 100), (200, 200), (100, 200)]
    ):
        # Generate the calibration scene
        self.calibration_scene = QGraphicsScene(self)
        self.calibration_scene.setSceneRect(0, 0, self.canvas_width, self.canvas_height)

        # Generate the calibration view
        self.calibration_view = QGraphicsView(self.calibration_scene)
        self.calibration_view.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # Disable scrollbars
        self.calibration_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.calibration_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Add the tetragon to the calibration scene
        self.vertices = []
        for x, y in tetragon_coords:
            vertex = QGraphicsEllipseItem(0, 0, 10, 10)
            vertex.setBrush(Qt.red)
            vertex.setFlag(QGraphicsEllipseItem.ItemIsMovable)
            vertex.setPos(x, y)
            self.vertices.append(vertex)
            self.calibration_scene.addItem(vertex)
            print(f"Vertex added at: ({x}, {y})")  # Debugging statement

        print(
            f"Scene Rect: {self.calibration_scene.sceneRect()}"
        )  # Debugging statement

        # Mouse tracking
        self.calibration_view.installEventFilter(self)
        self.setMouseTracking(True)

        # Add the view to the QStackedWidget
        self.stacked_widget.addWidget(self.calibration_view)

    def switch_to_shooting_scene(self):
        self.stacked_widget.setCurrentWidget(self.shooting_view)

    def switch_to_calibration_scene(self):
        self.stacked_widget.setCurrentWidget(self.calibration_view)

    def get_coordinates(self):
        return [vertex.pos() for vertex in self.vertices]

    def create_tetragon(self, tetragon_coords):
        # Add the tetragon to the calibration scene
        self.vertices = []
        for x, y in tetragon_coords:
            vertex = QGraphicsEllipseItem(x - 5, y - 5, 10, 10)
            vertex.setBrush(Qt.red)
            vertex.setFlag(QGraphicsEllipseItem.ItemIsMovable)
            self.vertices.append(vertex)
            vertex.setVisible(True)  # Show the item
            self.calibration_scene.addItem(vertex)

    def update_vertices(self, new_coordinates):
        # Check if the lengths of vertices and new_coordinates match
        if len(self.vertices) != len(new_coordinates):
            print("Error: Mismatch in the number of vertices and new coordinates")
            return
        for vertex, (x, y) in zip(self.vertices, new_coordinates):
            vertex.setPos(x, y)
            print(f'vertex pos: {vertex.pos()}')

    def eventFilter(self, source, event):
        "The mouse movements do not work without this function"
        self.calibration_mode = self.photom_controls.photom_assembly._calibrating
        if event.type() == QMouseEvent.MouseMove:
            pass
            if self._left_click_hold and not self.calibration_mode:
                # Move the mirror around if the left button is clicked
                self._move_marker_and_update_sliders()
            # Debugging statements
            # print('mouse move')
            # print(f'x1: {event.screenPos().x()}, y1: {event.screenPos().y()}')
            # print(f'x: {event.posF().x()}, y: {event.posF().y()}')
            # print(f'x: {event.localPosF().x()}, y: {event.localPosF().y()}')
            # print(f'x: {event.windowPosF().x()}, y: {event.windowPosF().y()}')
            # print(f'x: {event.screenPosF().x()}, y: {event.screenPosF().y()}')
            # print(f'x: {event.globalPosF().x()}, y: {event.globalPosF().y()}')
            # print(f'x2: {event.pos().x()}, y2: {event.pos().y()}')
        elif event.type() == QMouseEvent.MouseButtonPress:
            print('mouse button pressed')
            if self.calibration_mode:
                print('calibration mode')
                if event.buttons() == Qt.LeftButton:
                    self._left_click_hold = True
                    print('left button pressed')
                    # print(f'x: {event.posF().x()}, y: {event.posF().y()}')
                    print(f'x2: {event.pos().x()}, y2: {event.pos().y()}')
                elif event.buttons() == Qt.RightButton:
                    self._right_click_hold = True
                    print('right button pressed')
            else:
                print('shooting mode')
                if event.buttons() == Qt.LeftButton:
                    self._left_click_hold = True
                    print('left button pressed')
                    print(f'x2: {event.pos().x()}, y2: {event.pos().y()}')
                    self._move_marker_and_update_sliders()
                elif event.buttons() == Qt.RightButton:
                    self._right_click_hold = True
                    self.photom_controls.photom_assembly.laser[0].toggle_emission = True
                    print('right button pressed')
        elif event.type() == QMouseEvent.MouseButtonRelease:
            if self.calibration_mode:
                if event.button() == Qt.LeftButton:
                    self._left_click_hold = False
                    print('left button released')
                elif event.button() == Qt.RightButton:
                    self._right_click_hold = False
                    print('right button released')
            else:
                print('mouse button released')
                if event.button() == Qt.LeftButton:
                    print('left button released')
                    self._left_click_hold = False
                elif event.button() == Qt.RightButton:
                    self._right_click_hold = False
                    self.photom_controls.photom_assembly.laser[
                        0
                    ].toggle_emission = False
                    time.sleep(0.5)
                    print('right button released')

        return super(LaserMarkerWindow, self).eventFilter(source, event)

    def _move_marker_and_update_sliders(self):
        # Update the mirror slider values
        if self.photom_controls is not None:
            marker_position = [self.marker.pos().x(), self.marker.pos().y()]
            new_coords = self.photom_controls.mirror_widgets[
                self.photom_controls._current_mirror_idx
            ].mirror.affine_transform_obj.apply_affine(marker_position)
            self.photom_controls.mirror_widgets[
                self.photom_controls._current_mirror_idx
            ].mirror_x_slider.setValue(new_coords[0][0])
            self.photom_controls.mirror_widgets[
                self.photom_controls._current_mirror_idx
            ].mirror_y_slider.setValue(new_coords[1][0])

    def get_marker_center(self, marker):
        fm = QFontMetricsF(QFont())
        boundingRect = fm.tightBoundingRect(marker.text())
        mergintop = fm.ascent() + boundingRect.top()
        x = marker.pos().x() + boundingRect.left() + boundingRect.width() / 2
        y = marker.pos().y() + mergintop + boundingRect.height() / 2
        return x, y

    def display_marker_center(self, marker, coords=None):
        if coords is None:
            coords = (marker.x(), marker.y())

        if coords is None:
            coords = (marker.x(), marker.y())
        fm = QFontMetricsF(QFont())
        boundingRect = fm.tightBoundingRect(marker.text())
        mergintop = fm.ascent() + boundingRect.top()
        marker.setPos(
            coords[0] - boundingRect.left() - boundingRect.width() / 2,
            coords[1] - mergintop - boundingRect.height() / 2,
        )
        return marker


if __name__ == "__main__":
    import os

    if DEMO_MODE:
        from copylot.assemblies.photom.photom_mock_devices import (
            MockLaser,
            MockMirror,
            MockArduinoPWM,
        )

        Laser = MockLaser
        Mirror = MockMirror
        ArduinoPWM = MockArduinoPWM
    else:
        from copylot.hardware.mirrors.optotune.mirror import OptoMirror as Mirror
        from copylot.hardware.lasers.vortran.vortran import VortranLaser as Laser
        from copylot.assemblies.photom.utils.arduino import ArduinoPWM as ArduinoPWM

    config_path = r"./copylot/assemblies/photom/demo/photom_VIS_config.yml"

    # TODO: this should be a function that parses the config_file and returns the photom_assembly
    # Load the config file and parse it
    with open(config_path, "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
        lasers = [
            Laser(
                name=laser_data["name"],
                port=laser_data["COM_port"],
            )
            for laser_data in config["lasers"]
        ]
        mirrors = [
            Mirror(
                name=mirror_data["name"],
                com_port=mirror_data["COM_port"],
                pos_x=mirror_data["x_position"],
                pos_y=mirror_data["y_position"],
            )
            for mirror_data in config["mirrors"]
        ]  # Initial mirror position
        affine_matrix_paths = [
            mirror['affine_matrix_path'] for mirror in config['mirrors']
        ]
        arduino = [ArduinoPWM(serial_port='COM10', baud_rate=115200)]

        # Check that the number of mirrors and affine matrices match
        assert len(mirrors) == len(affine_matrix_paths)

    # Load photom assembly
    photom_assembly = PhotomAssembly(
        laser=lasers, mirror=mirrors, affine_matrix_path=affine_matrix_paths
    )

    # QT APP
    app = QApplication(sys.argv)

    # Define the positions and sizes for the windows
    screen_width = app.desktop().screenGeometry().width()
    screen_height = app.desktop().screenGeometry().height()
    ctrl_window_width = screen_width // 3  # Adjust the width as needed
    ctrl_window_height = screen_height // 3  # Use the full screen height

    if DEMO_MODE:
        camera_window = LaserMarkerWindow(
            name="Mock laser dots",
            window_size=(ctrl_window_width, ctrl_window_width),
            window_pos=(100, 100),
        )  # Set the positions of the windows
        ctrl_window = PhotomApp(
            photom_assembly=photom_assembly,
            photom_window_size=(ctrl_window_width, ctrl_window_width),
            photom_window_pos=(100, 100),
            demo_window=camera_window,
            arduino=arduino,
        )
        # Set the camera window to the calibration scene
        camera_window.switch_to_calibration_scene()
        rectangle_scaling = 0.2
        window_size = (camera_window.width(), camera_window.height())
        rectangle_size = (
            (window_size[0] * rectangle_scaling),
            (window_size[1] * rectangle_scaling),
        )
        rectangle_coords = calculate_rectangle_corners(rectangle_size)
        # translate each coordinate by the offset
        rectangle_coords = [(x + 30, y) for x, y in rectangle_coords]
        camera_window.update_vertices(rectangle_coords)
    else:
        # Set the positions of the windows
        ctrl_window = PhotomApp(
            photom_assembly=photom_assembly,
            photom_window_size=(ctrl_window_width, ctrl_window_width),
            photom_window_pos=(100, 100),
            arduino=arduino,
        )

    sys.exit(app.exec_())
