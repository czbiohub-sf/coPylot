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
    QSpinBox,
    QFileDialog,
    QLineEdit,
    QGridLayout,
    QProgressBar,
    QGraphicsRectItem,
    QGraphicsPixmapItem,
    QGraphicsPathItem,
)
from PyQt5.QtGui import (
    QColor,
    QPen,
    QFont,
    QFontMetricsF,
    QMouseEvent,
    QBrush,
    QPixmap,
    QResizeEvent,
    QPixmap,
    QPainterPath,
    QPainter,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from networkx import center

from copylot.assemblies.photom.photom import PhotomAssembly
from copylot.assemblies.photom.gui.utils import (
    CalibrationWithCameraThread,
    ClickablePixmapItem,
)

from typing import Tuple
import numpy as np
from copylot.assemblies.photom.gui.widgets import (
    LaserWidget,
    MirrorWidget,
    ArduinoPWMWidget,
)
import time
from copylot.assemblies.photom.utils.scanning_algorithms import (
    calculate_rectangle_corners,
)


# TODO: this one is hardcoded for now
from copylot.hardware.cameras.flir.flir_camera import FlirCamera


class PhotomApp(QMainWindow):
    def __init__(
        self,
        photom_assembly: PhotomAssembly,
        photom_sensor_size_yx: Tuple[int, int] = (2048, 2448),
        photom_window_size_x: int = 800,
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
        self.photom_window_size_x = photom_window_size_x
        self.photom_sensor_size_yx = photom_sensor_size_yx
        self.photom_window_pos = photom_window_pos
        self._current_mirror_idx = 0
        self._laser_window_transparency = 0.7
        self.scaling_matrix = np.eye(3)
        self.T_mirror_cam_matrix = np.eye(3)
        self.calibration_w_cam_thread = CalibrationWithCameraThread(
            self.photom_assembly, self._current_mirror_idx
        )
        self.calibration_w_cam_thread.finished.connect(self.done_calibration)
        self.imageWindows = []
        self.drawingTraces = []  # List to store traces
        self.currentTrace = []  # Current trace being drawn

        # if DEMO_MODE:
        #     self.demo_window = demo_window

        self.initializer_laser_marker_window()
        self.initialize_UI()

    def initializer_laser_marker_window(self):
        # Making the photom_window a square and display right besides the control UI
        window_pos = (
            self.photom_window_size_x + self.photom_window_pos[0],
            self.photom_window_pos[1],
        )
        self.photom_window = LaserMarkerWindow(
            photom_controls=self,
            name='Laser Marker',
            sensor_size_yx=self.photom_sensor_size_yx,
            fixed_width=self.photom_window_size_x,
            window_pos=window_pos,
        )
        self.aspect_ratio = (
            self.photom_sensor_size_yx[1] / self.photom_sensor_size_yx[0]
        )
        calculated_height = self.photom_window_size_x / self.aspect_ratio
        self.scaling_factor_x = (
            self.photom_sensor_size_yx[1] / self.photom_window_size_x
        )
        self.scaling_factor_y = self.photom_sensor_size_yx[0] / calculated_height
        # TODO: the affine transforms are in XY coordinates. Need to change to YX
        self.scaling_matrix = np.array(
            [[self.scaling_factor_x, 0, 1], [0, self.scaling_factor_y, 1], [0, 0, 1]]
        )
        self.photom_window.windowClosed.connect(
            self.closeAllWindows
        )  # Connect the signal to slot

    def initialize_UI(self):
        """
        Initialize the UI.

        """
        self.setGeometry(
            self.photom_window_pos[0],
            self.photom_window_pos[1],
            self.photom_window_size_x,
            self.photom_window_size_x,
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

        # Resize QSpinBox
        self.resize_spinbox = QSpinBox()
        self.resize_spinbox.setRange(50, 200)  # Set range from 50% to 200%
        self.resize_spinbox.setSuffix("%")  # Add a percentage sign as suffix
        self.resize_spinbox.setValue(100)  # Default value is 100%
        self.resize_spinbox.valueChanged.connect(self.resize_laser_marker_window)
        self.resize_spinbox.editingFinished.connect(self.resize_laser_marker_window)
        transparency_layout.addWidget(QLabel("Resize Window:"))
        transparency_layout.addWidget(self.resize_spinbox)

        # Set the transparency group layout
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
            arduino_pwm_widget = ArduinoPWMWidget(self.photom_assembly, arduino, self)
            self.arduino_pwm_widgets.append(arduino_pwm_widget)
            arduino_layout.addWidget(arduino_pwm_widget)
        arduino_group.setLayout(arduino_layout)

        # Add the laser and mirror group boxes to the main layout
        main_layout = QVBoxLayout()

        self.game_mode_button = QPushButton("Game Mode: OFF", self)
        self.game_mode_button.setCheckable(True)  # Make the button toggleable
        self.game_mode_button.clicked.connect(self.toggle_game_mode)

        self.toggle_drawing_mode_button = QPushButton("Toggle Drawing Mode", self)
        self.toggle_drawing_mode_button.clicked.connect(self.toggleDrawingMode)
        self.playButton = QPushButton("Play", self)
        self.playButton.clicked.connect(self.play_drawing)
        self.playButton.hide()  # Initially hide the Play button

        main_layout.addWidget(transparency_group)
        main_layout.addWidget(self.game_mode_button)
        main_layout.addWidget(self.toggle_drawing_mode_button)
        main_layout.addWidget(self.playButton)
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
        self.calibrate_button.clicked.connect(self.calibrate_w_camera)
        main_layout.addWidget(self.calibrate_button)

        self.load_calibration_button = QPushButton("Load Calibration")
        self.load_calibration_button.clicked.connect(self.load_calibration)
        main_layout.addWidget(self.load_calibration_button)

        # Add a "Cancel Calibration" button (initially hidden)
        self.cancel_calibration_button = QPushButton("Cancel Calibration")
        self.cancel_calibration_button.clicked.connect(self.cancel_calibration)
        self.cancel_calibration_button.hide()
        main_layout.addWidget(self.cancel_calibration_button)
        main_widget = QWidget(self)
        main_widget.setLayout(main_layout)

        self.setCentralWidget(main_widget)
        self.show()

    def toggle_game_mode(self, checked):
        if checked:
            self.game_mode_button.setText("Game Mode: ON")
            self.photom_window.game_mode = True
        else:
            self.game_mode_button.setText("Game Mode: OFF")
            self.photom_window.game_mode = False

    def toggleDrawingMode(self):
        # Call the method to toggle the drawing scene on the LaserMarkerWindow
        if (
            self.photom_window.stacked_widget.currentWidget()
            == self.photom_window.drawing_view
        ):
            # If in drawing mode, clear the drawing before switching
            self.photom_window.clearDrawing()
            self.playButton.hide()
        else:
            self.playButton.show()
        self.photom_window.toggleDrawingScene()

    def resize_laser_marker_window(self):
        # Retrieve the selected resize percentage from the QSpinBox
        percentage = self.resize_spinbox.value() / 100.0

        # Calculate the new width based on the selected percentage
        new_width = int(self.photom_window_size_x * percentage)
        # Calculate the new height to maintain the aspect ratio
        new_height = int(new_width / self.photom_window.aspect_ratio)

        self.photom_window.update_window_geometry(new_width, new_height)

        # Update the scaling transform matrix based on window size
        self.scaling_factor_x = self.photom_sensor_size_yx[1] / new_width
        self.scaling_factor_y = self.photom_sensor_size_yx[0] / new_height
        self.scaling_matrix = np.array(
            [[self.scaling_factor_x, 0, 1], [0, self.scaling_factor_y, 1], [0, 0, 1]]
        )
        T_compose_mat = self.T_mirror_cam_matrix @ self.scaling_matrix
        self.photom_assembly.mirror[
            self._current_mirror_idx
        ].affine_transform_obj.set_affine_matrix(T_compose_mat)

    def mirror_dropdown_changed(self, index):
        print(f"Mirror dropdown changed to index {index}")
        self._current_mirror_idx = index

        # Reset to (0,0) position
        self.photom_assembly.mirror[self._current_mirror_idx].position = [0, 0]

    def recenter_marker(self):
        self.photom_window.recenter_marker()

    def calibrate_w_camera(self):
        print("Calibrating with camera...")
        # Hide the calibrate button
        self.calibrate_button.hide()
        self.load_calibration_button.hide()
        # Show the "Cancel Calibration" button
        self.cancel_calibration_button.show()

        # if DEMO_MODE:
        #     print(f'Calibrating mirror: {self._current_mirror_idx}')
        # else:
        # TODO: Hardcoding the camera and coordinates of mirror for calib. Change this after
        self.setup_calibration()
        self.photom_assembly.mirror[
            self._current_mirror_idx
        ].affine_transform_obj.reset_T_affine()
        self.calibration_w_cam_thread.start()

    # TODO: these parameters are currently hardcoded
    def setup_calibration(self):
        # Open the camera and add it to the assembly
        cam = FlirCamera()
        cam.open()
        self.photom_assembly.camera = [cam]

        self.photom_assembly.laser[0].power = 0.0
        self.photom_assembly.laser[0].toggle_emission = True
        self.photom_assembly.laser[0].power = 30.0

    def load_calibration(self):
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
            # Scale the matrix calculated from calibration to match the photom laser window
            self.T_mirror_cam_matrix = self.photom_assembly.mirror[
                self._current_mirror_idx
            ].affine_transform_obj.get_affine_matrix()
            T_compose_mat = self.T_mirror_cam_matrix @ self.scaling_matrix
            self.photom_assembly.mirror[
                self._current_mirror_idx
            ].affine_transform_obj.set_affine_matrix(T_compose_mat)
            print("Scaled matrix:", T_compose_mat)
            self.photom_window.switch_to_shooting_scene()
            self.photom_window.marker.show()

    def cancel_calibration(self):
        # Implement your cancel calibration function here
        print("Canceling calibration...")
        # Show the "Calibrate" button
        self.calibrate_button.show()
        self.load_calibration_button.show()
        # Show the "X" marker in photom_window
        self.photom_window.marker.show()

        self.cancel_calibration_button.hide()
        # Switch back to the shooting scene
        self.photom_window.switch_to_shooting_scene()

    def display_saved_plot(self, plot_path):
        # This function assumes that a QApplication instance is already running
        image_window = ImageWindow(plot_path)
        image_window.show()
        self.imageWindows.append(image_window)
        # return image_window

    def done_calibration(self, T_affine, plot_save_path):
        # Unload the camera
        self.photom_assembly.camera[0].close()
        self.photom_assembly.camera = []

        # Show plot and update matrix
        self.display_saved_plot(plot_save_path)
        self.T_mirror_cam_matrix = T_affine

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
                matrix=self.T_mirror_cam_matrix, config_file=typed_filename
            )
            self.photom_window.switch_to_shooting_scene()
            self.photom_window.marker.show()

            # Hide the "Done Calibration" button
            self.calibrate_button.show()
            self.cancel_calibration_button.hide()

            # Update the affine to match the photom laser window
            self.update_laser_window_affine()

            # if DEMO_MODE:
            #     NotImplementedError("Demo Mode: Calibration not implemented yet.")
        else:
            print("No file selected. Skiping Saving the calibration matrix.")
            # Show dialog box saying no file selected
        print("Calibration done")
        center_coords = [
            self.photom_sensor_size_yx[0] / 2,
            self.photom_sensor_size_yx[1] / 2,
        ]
        self.photom_assembly.set_position(self._current_mirror_idx, center_coords)

    def update_laser_window_affine(self):
        # Update the scaling transform matrix
        print('updating laser window affine')
        self.scaling_factor_x = (
            self.photom_sensor_size_yx[1] / self.photom_window_size_x
        )
        self.scaling_factor_y = (
            self.photom_sensor_size_yx[0] / self.photom_window_size_x
        )
        self.scaling_matrix = np.array(
            [[self.scaling_factor_x, 0, 1], [0, self.scaling_factor_y, 1], [0, 0, 1]]
        )
        T_compose_mat = self.T_mirror_cam_matrix @ self.scaling_matrix
        self.photom_assembly.mirror[
            self._current_mirror_idx
        ].affine_transform_obj.set_affine_matrix(T_compose_mat)
        print(f'Updated affine matrix: {T_compose_mat}')

    def update_transparency(self, value):
        transparency_percent = value
        self.transparency_label.setText(f"Transparency: {transparency_percent}%")
        opacity = 1.0 - (transparency_percent / 100.0)  # Calculate opacity (0.0 to 1.0)
        self.photom_window.setWindowOpacity(opacity)  # Update photom_window opacity

    def play_drawing(self):
        for trace in self.photom_window.drawingTraces:
            print(f'Playing trace: {trace}')
            self.photom_assembly.set_position(self._current_mirror_idx, trace)

    def display_rectangle(self):
        self.photom_window.switch_to_calibration_scene()

    def closeEvent(self, event):
        self.closeAllWindows()  # Ensure closing main window closes everything
        super().closeEvent(event)

    def closeAllWindows(self):
        self.photom_window.close()
        self.close()
        QApplication.quit()  # Quit the application


class LaserMarkerWindow(QMainWindow):
    windowClosed = pyqtSignal()  # Define the signal

    def __init__(
        self,
        photom_controls: QMainWindow = None,
        name="Laser Marker",
        sensor_size_yx: Tuple = (2048, 2048),
        window_pos: Tuple = (100, 100),
        fixed_width: int = 800,
    ):
        super().__init__()
        self.photom_controls = photom_controls
        self.window_name = name
        self.aspect_ratio = sensor_size_yx[1] / sensor_size_yx[0]
        self.fixed_width = fixed_width
        calculated_height = int(self.fixed_width / self.aspect_ratio)
        self.window_pos = window_pos
        self.window_geometry = self.window_pos + (self.fixed_width, calculated_height)
        self.setMouseTracking(True)
        self.setWindowOpacity(self.photom_controls._laser_window_transparency)
        self.game_mode = False  # Default to off
        # Create a QStackedWidget
        # TODO: do we need the stacked widget?
        self.stacked_widget = QStackedWidget()
        # Set the QStackedWidget as the central widget
        self.initialize_UI()
        self.initMarker()
        self.initDrawingScene()

        self.lastPoint = None
        self.drawing = False
        self.drawingTraces = []  # To store lists of traces
        self.currentTrace = []  # To store points of the current trace being drawn

        tetragon_coords = calculate_rectangle_corners(
            [self.window_geometry[-2] / 5, self.window_geometry[-1] / 5],
            center=[self.window_geometry[-2] / 2, self.window_geometry[-1] / 2],
        )
        self.init_tetragon(tetragon_coords=tetragon_coords)

        self.setCentralWidget(self.stacked_widget)

        self.switch_to_shooting_scene()

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
        # self.sidebar_size = self.frameGeometry().width() - self.window_geometry[2]
        # self.topbar_size = self.frameGeometry().height() - self.window_geometry[3]
        # self.canvas_width = self.frameGeometry().width() - self.sidebar_size
        # self.canvas_height = self.frameGeometry().height() - self.topbar_size

        # print(f'sidebar size: {self.sidebar_size}, topbar size: {self.topbar_size}')
        # print(f'canvas width: {self.canvas_width}, canvas height: {self.canvas_height}')

    def update_window_geometry(self, new_width, new_height):
        self.window_geometry = self.window_pos + (new_width, new_height)
        self.shooting_view.setFixedSize(new_width, new_height)
        self.shooting_scene.setSceneRect(0, 0, new_width, new_height)
        self.setFixedSize(new_width, new_height)

    def recenter_marker(self):
        self.display_marker_center(
            self.marker,
            (self.window_geometry[-2] / 2, self.window_geometry[-1] / 2),
        )

    def initMarker(self):
        # Generate the shooting scene
        self.shooting_scene = QGraphicsScene(self)
        self.shooting_scene.setSceneRect(
            0, 0, self.window_geometry[-2], self.window_geometry[-1]
        )

        # Generate the shooting view
        self.shooting_view = QGraphicsView(self.shooting_scene)
        self.shooting_view.setMouseTracking(True)
        self.setCentralWidget(self.shooting_view)
        self.shooting_view.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.shooting_view.setFixedSize(
            self.window_geometry[-2], self.window_geometry[-1]
        )

        # Mouse tracking
        self.shooting_view.installEventFilter(self)
        self.shooting_view.viewport().installEventFilter(self)
        self.setMouseTracking(True)
        # self.marker = QGraphicsSimpleTextItem("+")
        # self.marker.setBrush(QColor(255, 0, 0))
        # Load the PNG image
        pixmap = QPixmap(r'./copylot/assemblies/photom/utils/images/hit_marker_red.png')
        assert pixmap.isNull() == False
        pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Create a QGraphicsPixmapItem with the loaded image
        self.marker = ClickablePixmapItem(pixmap)
        self.marker.setFlag(QGraphicsItem.ItemIsMovable, True)

        # # Set larger font size
        # font = self.marker.font()
        # font.setPointSize(30)
        # self.marker.setFont(font)

        # Position the marker
        self.display_marker_center(
            self.marker, (self.window_geometry[-2] / 2, self.window_geometry[-1] / 2)
        )

        self.shooting_scene.addItem(self.marker)

        ## Add the rectangle
        rect_width = 2 * self.window_geometry[-2] / 3
        rect_height = 2 * self.window_geometry[-1] / 3
        rect_x = (self.window_geometry[-2] - rect_width) / 2
        rect_y = (self.window_geometry[-1] - rect_height) / 2
        # Continue from the previous code in initMarker...
        pen = QPen(QColor(0, 0, 0))
        pen.setStyle(Qt.DashLine)  # Dashed line style
        pen.setWidth(2)  # Set the pen width

        # Create the rectangle with no fill (transparent)
        self.dashed_rectangle = QGraphicsRectItem(
            rect_x, rect_y, rect_width, rect_height
        )
        self.dashed_rectangle.setPen(pen)
        self.dashed_rectangle.setBrush(QBrush(Qt.transparent))  # Transparent fill
        # Add the rectangle to the scene
        self.shooting_scene.addItem(self.dashed_rectangle)

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
        self.calibration_scene.setSceneRect(
            0, 0, self.window_geometry[-2], self.window_geometry[-1]
        )

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

    def initDrawingScene(self):
        # Initialize the drawing scene
        self.drawing_scene = QGraphicsScene()
        self.drawing_scene.setSceneRect(
            0, 0, self.window_geometry[-2], self.window_geometry[-1]
        )

        # Initialize the drawing view
        self.drawing_view = QGraphicsView(self.drawing_scene)
        self.drawing_view.setFixedSize(
            self.window_geometry[-2], self.window_geometry[-1]
        )

        # Disable scrollbars
        self.drawing_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.drawing_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Mouse tracking
        self.drawing_view.setMouseTracking(True)
        self.drawing_view.installEventFilter(self)
        self.drawing_view.viewport().installEventFilter(self)

        # Add a drawable pixmap item to the scene
        self.drawablePixmapItem = QGraphicsPixmapItem()
        self.drawing_scene.addItem(self.drawablePixmapItem)
        # Initialize the pixmap with a transparent background of the same size as the scene
        self.drawablePixmap = QPixmap(
            self.window_geometry[-2], self.window_geometry[-1]
        )
        self.drawablePixmap.fill(Qt.transparent)  # Fill with transparent color
        self.drawablePixmapItem.setPixmap(self.drawablePixmap)

        # Add the drawing view to the stacked widget
        self.stacked_widget.addWidget(self.drawing_view)

    def switchToDrawingScene(self):
        # Method to switch to the drawing scene
        self.stacked_widget.setCurrentWidget(self.drawing_view)

    def switch_to_shooting_scene(self):
        self.stacked_widget.setCurrentWidget(self.shooting_view)

    def switch_to_calibration_scene(self):
        self.stacked_widget.setCurrentWidget(self.calibration_view)

    def toggleDrawingScene(self):
        # Check which scene is currently active and switch to the other
        if self.stacked_widget.currentWidget() == self.drawing_view:
            self.switch_to_shooting_scene()  # Assuming this is the method to switch back to your original scene
        else:
            self.switchToDrawingScene()

    def clearDrawing(self):
        # Clear the drawing by filling the pixmap with transparent color
        self.drawablePixmap.fill(Qt.transparent)
        self.drawablePixmapItem.setPixmap(self.drawablePixmap)

        # Reset the traces
        self.drawingTraces = []
        self.currentTrace = []

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
        if event.type() == QMouseEvent.MouseMove:
            pass
            if self._left_click_hold:
                if source == self.shooting_view.viewport():
                    self._move_marker_and_update_sliders()
                elif self.drawing and source == self.drawing_view.viewport():
                    painter = QPainter(self.drawablePixmap)
                    pen = QPen(Qt.black, 2, Qt.SolidLine)
                    painter.setPen(pen)
                    # Convert event positions to scene positions
                    lastScenePos = self.drawing_view.mapToScene(self.lastPoint)
                    currentScenePos = self.drawing_view.mapToScene(event.pos())
                    painter.drawLine(lastScenePos, currentScenePos)
                    painter.end()  # End the painter to apply the drawing

                    self.lastPoint = event.pos()
                    self.drawablePixmapItem.setPixmap(self.drawablePixmap)
                    self.currentTrace.append((currentScenePos.x(), currentScenePos.y()))

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
            print('shooting mode')
            if event.buttons() == Qt.LeftButton:
                print('left button pressed')
                print(f'x2: {event.pos().x()}, y2: {event.pos().y()}')
                self._left_click_hold = True
                if self.stacked_widget.currentWidget() == self.drawing_view:
                    self.drawing = True
                    self.lastPoint = event.pos()
                elif self.stacked_widget.currentWidget() == self.shooting_view:
                    self._move_marker_and_update_sliders()
            elif event.buttons() == Qt.RightButton:
                self._right_click_hold = True
                self.photom_controls.photom_assembly.laser[0].toggle_emission = True
                print('right button pressed')
        elif event.type() == QMouseEvent.MouseButtonRelease:
            print('mouse button released')
            if event.button() == Qt.LeftButton:
                print('left button released')
                self._left_click_hold = False
                if self.drawing:
                    self.drawing = False
                    self.drawingTraces.append(self.currentTrace)
                    self.currentTrace = []
            elif event.button() == Qt.RightButton:
                self._right_click_hold = False
                self.photom_controls.photom_assembly.laser[0].toggle_emission = False
                if self.game_mode:
                    self._game_mode_marker(event)
                time.sleep(0.3)
                print('right button released')

        return super(LaserMarkerWindow, self).eventFilter(source, event)

    # Triggered after manual resizing or calling window.setGeometry()
    def resizeEvent(self, a0: QResizeEvent | None) -> None:
        super().resizeEvent(a0)
        rect = self.shooting_view.sceneRect()
        self.shooting_scene.setSceneRect(0, 0, rect.width(), rect.height())
        print(f'resize event: {rect.width()}, {rect.height()}')
        self._update_scene_items(rect.width(), rect.height())

    def remove_score_text(self, text_item):
        self.shooting_scene.removeItem(text_item)

    def _game_mode_marker(self, event: QMouseEvent):
        # Show "+100" at click position
        score_text = QGraphicsSimpleTextItem("+100")
        score_text.setBrush(QColor(255, 255, 0))  # Yellow color for visibility
        # Set a larger font size
        font = QFont()
        font.setPointSize(30)  # Set the font size to 24 points
        score_text.setFont(font)
        score_text.setPos(
            event.pos().x() + 15, event.pos().y() - 70
        )  # Position at click
        self.shooting_scene.addItem(score_text)
        # Create a QTimer to remove the "+100" after 1 second
        QTimer.singleShot(1000, lambda: self.remove_score_text(score_text))

    def _update_scene_items(self, new_width, new_height):
        # Dahsed rectangle
        rect_width = new_width * 2 / 3  # Example: 2/3 of the new width
        rect_height = new_height * 2 / 3  # Example: 2/3 of the new height
        rect_x = (new_width - rect_width) / 2
        rect_y = (new_height - rect_height) / 2

        # Re-center the "X" marker
        marker_center_x = new_width / 2
        marker_center_y = new_height / 2
        self.recenter_marker()

        # resize the rectangle
        self.dashed_rectangle.setRect(rect_x, rect_y, rect_width, rect_height)
        pen = QPen(
            QColor(0, 0, 0), 2, Qt.DashLine
        )  # Example: black color, width 2, dashed line
        self.dashed_rectangle.setPen(pen)
        self.shooting_view.update()

    def _move_marker_and_update_sliders(self):
        # Update the mirror slider values
        if self.photom_controls is not None:
            marker_position = self.get_marker_center(
                self.marker, coords=(self.marker.pos().x(), self.marker.pos().y())
            )
            # marker_position = [self.marker.pos().x(), self.marker.pos().y()]
            new_coords = self.photom_controls.mirror_widgets[
                self.photom_controls._current_mirror_idx
            ].mirror.affine_transform_obj.apply_affine(marker_position)
            self.photom_controls.mirror_widgets[
                self.photom_controls._current_mirror_idx
            ].mirror_x_slider.setValue(new_coords[0][0])
            self.photom_controls.mirror_widgets[
                self.photom_controls._current_mirror_idx
            ].mirror_y_slider.setValue(new_coords[1][0])

    def get_marker_center(self, marker, coords=None):
        if coords is None:
            coords = (marker.x(), marker.y())
        center_x = coords[0] + marker.pixmap().width() / 2
        center_y = coords[1] + marker.pixmap().height() / 2
        return [center_x, center_y]

    def display_marker_center(self, marker, coords=None):
        if coords is None:
            coords = (marker.x(), marker.y())
        center_x = coords[0] - marker.pixmap().width() / 2
        center_y = coords[1] - marker.pixmap().height() / 2
        marker.setPos(center_x, center_y)

    def closeEvent(self, event):
        self.windowClosed.emit()  # Emit the signal when the window is about to close
        super().closeEvent(event)  # Proceed with the default close event


class ImageWindow(QMainWindow):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calibration Overlay of laser grid and MIP points")

        # Create a label and set its pixmap to the image at image_path
        self.label = QLabel(self)
        self.pixmap = QPixmap(image_path)

        # Resize the label to fit the pixmap
        self.label.setPixmap(self.pixmap)
        self.label.resize(self.pixmap.width(), self.pixmap.height())

        # Resize the window to fit the label (plus a little margin if desired)
        self.resize(
            self.pixmap.width() + 20, self.pixmap.height() + 20
        )  # Adding a 20-pixel margin

        # Optionally, center the window on the screen
        self.center()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(
            QApplication.desktop().cursor().pos()
        )
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())
