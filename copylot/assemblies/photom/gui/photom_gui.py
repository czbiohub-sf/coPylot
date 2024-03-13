import sys
import yaml

from copylot.assemblies.photom.utils.scanning_algorithms import (
    calculate_rectangle_corners,
)
from copylot.assemblies.photom.photom import PhotomAssembly

from copylot.assemblies.photom.gui.windows import LaserMarkerWindow, PhotomApp
from PyQt5.QtWidgets import QApplication


def load_config(config: str):
    assert config.endswith(".yml"), "Config file must be a .yml file"
    # TODO: this should be a function that parses the config_file and returns the photom_assembly
    # Load the config file and parse it
    with open(config_path, "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    return config


def make_photom_assembly(config):
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
    affine_matrix_paths = [mirror['affine_matrix_path'] for mirror in config['mirrors']]

    # Check that the number of mirrors and affine matrices match
    assert len(mirrors) == len(affine_matrix_paths)

    # Load photom assembly
    photom_assembly = PhotomAssembly(
        laser=lasers, mirror=mirrors, affine_matrix_path=affine_matrix_paths
    )
    return photom_assembly


if __name__ == "__main__":
    DEMO_MODE = False
    # TODO: grab the actual value if the camera is connected to photom_assmebly
    CAMERA_SENSOR_YX = (2048, 2448)

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
    config = load_config(config_path)
    photom_assembly = make_photom_assembly(config)

    # QT APP
    app = QApplication(sys.argv)
    # Define the positions and sizes for the windows
    screen_width = app.desktop().screenGeometry().width()
    screen_height = app.desktop().screenGeometry().height()
    ctrl_window_width = screen_width // 3  # Adjust the width as needed
    ctrl_window_height = screen_height // 3  # Use the full screen height

    arduino = [ArduinoPWM(serial_port='COM10', baud_rate=115200)]

    if DEMO_MODE:
        camera_window = LaserMarkerWindow(
            name="Mock laser dots",
            sensor_size_yx=(2048, 2048),
            window_pos=(100, 100),
            fixed_width=ctrl_window_width,
        )  # Set the positions of the windows
        ctrl_window = PhotomApp(
            photom_assembly=photom_assembly,
            photom_sensor_size_yx=CAMERA_SENSOR_YX,
            photom_window_size_x=ctrl_window_width,
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
            photom_sensor_size_yx=CAMERA_SENSOR_YX,
            photom_window_size_x=ctrl_window_width,
            photom_window_pos=(100, 100),
            arduino=arduino,
        )

    sys.exit(app.exec_())
