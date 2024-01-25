import sys
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
)
from PyQt5.QtGui import QColor, QPen, QFont, QFontMetricsF, QMouseEvent
from copylot.assemblies.photom.utils.scanning_algorithms import (
    calculate_rectangle_corners,
)
from copylot.assemblies.photom.utils.qt_utils import DoubleSlider
import numpy as np
from copylot.assemblies.photom.photom import PhotomAssembly
from typing import Any, Tuple

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
        self.emission_delay = 0.0

        self._curr_power = 0.0
        self._slider_decimal = 1

        self.initializer_laser()
        self.initialize_UI()

    def initializer_laser(self):
        self.laser.toggle_emission = self.emission_state
        self.laser.power = self._curr_power
        self.laser.emission_delay = self.emission_delay

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
        self.power_label = QLabel(f"Power: {self._curr_power} %")
        layout.addWidget(self.power_label)

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
        self.laser.power = value / (10**self._slider_decimal)
        self._curr_power = self.laser.power
        # Update the QLabel with the new power value
        self.power_label.setText(f"Power: {self._curr_power} %")


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


class PhotomApp(QMainWindow):
    def __init__(
        self,
        photom_assembly: PhotomAssembly,
        photom_window_size: Tuple[int, int] = (400, 500),
        photom_window_pos: Tuple[int, int] = (100, 100),
        demo_window=None,
    ):
        super().__init__()

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

        # Add the laser and mirror group boxes to the main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(transparency_group)
        main_layout.addWidget(laser_group)
        main_layout.addWidget(mirror_group)

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
        mirror_calib_size = self.photom_assembly._calibration_rectangle_size_xy
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
        # logger.debug(f"Affine matrix: {T_affine}")
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
                if event.buttons() == Qt.LeftButton:
                    self._left_click_hold = False
                    print('left button released')
                elif event.buttons() == Qt.RightButton:
                    self._right_click_hold = False
                    print('right button released')
            else:
                print('mouse button released')
                if event.buttons() == Qt.LeftButton:
                    self._left_click_hold = False
                    print('left button released')
                elif event.buttons() == Qt.RightButton:
                    print('right button released')
                    self._right_click_hold = False
                    self.photom_controls.photom_assembly.laser[
                        0
                    ].toggle_emission = False

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
        from copylot.assemblies.photom.photom_mock_devices import MockLaser, MockMirror

        Laser = MockLaser
        Mirror = MockMirror

    else:
        from copylot.hardware.mirrors.optotune.mirror import OptoMirror as Mirror
        from copylot.hardware.lasers.vortran.vortran import VortranLaser as Laser

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
        )

    sys.exit(app.exec_())
