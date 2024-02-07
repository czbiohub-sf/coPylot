from copylot.hardware.cameras.abstract_camera import AbstractCamera
from copylot.hardware.mirrors.abstract_mirror import AbstractMirror
from copylot.hardware.lasers.abstract_laser import AbstractLaser
from copylot.hardware.stages.abstract_stage import AbstractStage
from copylot.hardware.daqs.abstract_daq import AbstractDAQ
from copylot.assemblies.photom.utils.affine_transform import AffineTransform
from copylot.assemblies.photom.utils.scanning_algorithms import (
    calculate_rectangle_corners,
    generate_grid_points,
)
from pathlib import Path
from copylot import logger
from typing import Tuple
import time
from typing import Optional
import numpy as np
import tifffile
from copylot.assemblies.photom.utils import image_analysis as ia

# TODO: add the logger from copylot
# TODO: add mirror's confidence ROI or update with calibration in OptotuneDocumentation


class PhotomAssembly:
    def __init__(
        self,
        laser: list[AbstractLaser],
        mirror: list[AbstractMirror],
        affine_matrix_path: list[Path],
        camera: Optional[list[AbstractCamera]] = None,
        dac: Optional[list[AbstractDAQ]] = None,
    ):
        # hardware
        self.camera = camera
        self.laser = laser  # list of lasers
        self.mirror = mirror
        self.DAC = dac
        self.affine_matrix_path = affine_matrix_path
        self._calibrating = False
        # TODO: These are hardcoded values. Unsure if they should come from a config file
        self._calibration_rectangle_boundaries = None

    def init_mirrors(self):
        assert len(self.mirror) == len(self.affine_matrix_path)

        self._calibration_rectangle_boundaries = np.zeros((len(self.mirror), 2, 2))
        # Apply AffineTransform to each mirror
        for i in range(len(self.mirror)):
            self.mirror[i].affine_transform_obj = AffineTransform(
                config_file=self.affine_matrix_path[i]
            )
            self._calibration_rectangle_boundaries[i] = [[None, None], [None, None]]

    # TODO probably will replace the camera with zyx or yx image array input
    ## Camera Functions
    def capture(self, camera_index: int, exposure_time: float) -> list:
        pass

    ## Mirror Functions
    def stop_mirror(self, mirror_index: int):
        if mirror_index < len(self.mirror):
            self._calibrating = False
        else:
            raise IndexError("Mirror index out of range.")

    def get_position(self, mirror_index: int) -> list[float]:
        if mirror_index < len(self.mirror):
            if self.DAC is not None:
                raise NotImplementedError("No DAC found.")
            else:
                position = self.mirror[mirror_index].position
                return list(position)
        else:
            raise IndexError("Mirror index out of range.")

    def set_position(self, mirror_index: int, position: list[float]):
        if mirror_index < len(self.mirror):
            if self.DAC is not None:
                raise NotImplementedError("No DAC found.")
            else:
                # TODO: logic for applying the affine transform to the position
                print(f'postion before affine transform: {position}')
                new_position = self.mirror[
                    mirror_index
                ].affine_transform_obj.apply_affine(position)
                print(
                    f'postion after affine transform: {new_position[0]}{new_position[1]}'
                )
                self.mirror[mirror_index].position = [
                    new_position[0][0],
                    new_position[1][0],
                ]
        else:
            raise IndexError("Mirror index out of range.")

    def calibrate(
        self, mirror_index: int, rectangle_size_xy: tuple[int, int], center=[0.0, 0.0]
    ):
        if mirror_index < len(self.mirror):
            print("Calibrating mirror...")
            rectangle_coords = calculate_rectangle_corners(rectangle_size_xy, center)
            # offset the rectangle coords by the center
            # iterate over each corner and move the mirror
            i = 0
            while self._calibrating:
                # Logic for calibrating the mirror
                self.set_position(mirror_index, rectangle_coords[i])
                time.sleep(1)
                i += 1
                if i == 4:
                    i = 0
                    time.sleep(1)
            # moving the mirror in a rectangle
        else:
            raise IndexError("Mirror index out of range.")

    def calibrate_w_camera(
        self,
        mirror_index: int,
        camera_index: int,
        rectangle_boundaries: Tuple[Tuple[int, int], Tuple[int, int]],
        config_file: Path = './affine_matrix.yml',
        save_calib_stack_path: Path = None,
    ):
        assert self.camera is not None
        assert config_file.endswith('.yaml')
        self._calibration_rectangle_boundaries[mirror_index] = rectangle_boundaries

        x_min, x_max, y_min, y_max = self.camera.image_size_limits
        # assuming the minimum is always zero, which is typically that case
        assert mirror_index < len(self.mirror)
        assert camera_index < len(self.camera)
        print("Calibrating mirror_idx <{mirror_idx}> with camera_idx <{camera_idx}>")
        # TODO: replace these values with something from the config
        # Generate grid of points
        grid_points = generate_grid_points(
            rectangle_size=rectangle_boundaries, n_points=5
        )
        # Acquire sequence of images with points
        img_sequence = np.zeros((len(grid_points), x_max, y_max))
        for idx, coord in enumerate(grid_points):
            self.set_position(mirror_index, coord)
            img_sequence[idx] = self.camera[camera_index].snap()

        # Find the coordinates of peak per image
        peak_coords = np.zeros((len(grid_points), 2))
        for idx, img in enumerate(img_sequence):
            peak_coords[idx] = ia.find_objects_centroids(
                img, sigma=5, threshold_rel=0.5, min_distance=10
            )

        # Find the affine transform
        T_affine = self.mirror[mirror_index].affine_transform_obj.get_affine_matrix(
            peak_coords, grid_points
        )
        print(f"Affine matrix: {T_affine}")

        # Save the matrix
        config_file = Path(config_file)
        if not config_file.exists():
            config_file.mkdir(parents=True, exist_ok=True)

        self.photom_assembly.mirror[
            self._current_mirror_idx
        ].affine_transform_obj.save_matrix(matrix=T_affine, config_file=config_file)

        if save_calib_stack_path is not None:
            save_calib_stack_path = Path(save_calib_stack_path)
            save_calib_stack_path = Path(save_calib_stack_path)
            if not save_calib_stack_path.exists():
                save_calib_stack_path.mkdir(parents=True, exist_ok=True)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_path_name = (
                save_calib_stack_path / f'calibration_images_{timestamp}.tif'
            )
            tifffile.imwrite(output_path_name)

    ## LASER Fuctions
    def get_laser_power(self, laser_index: int) -> float:
        power = self.laser[laser_index].power
        return power

    def set_laser_power(self, laser_index: int, power: float):
        self.laser[laser_index].power = power

    ## Functions to convert between image coordinates and mirror coordinates or to DAC voltages
    def normalize(self, value, min_val, max_val):
        # Error handling for division by zero
        if max_val == min_val:
            raise ValueError("Maximum and minimum values cannot be the same")
        return (value - min_val) / (max_val - min_val)

    def convert_values(
        self, input_values: list, input_range: list, output_range: list
    ) -> list:
        """
        Converts a list of input values from one range to another
        input_values: list of values to convert
        input_range: list containing the minimum and maximum values of the input range
        output_range: list containing the minimum and maximum values of the output range

        Returns a list of converted values
        """
        # Error handling for incorrect range definitions
        if not (len(input_range) == 2 and len(output_range) == 2):
            raise ValueError(
                "Input and output ranges must each contain exactly two elements"
            )
        if not (input_range[0] < input_range[1] and output_range[0] < output_range[1]):
            raise ValueError(
                "In both ranges, the first element must be less than the second"
            )

        # input_values is not a list make a list
        if not isinstance(input_values, list):
            input_values = [input_values]

        # Precompute range differences
        input_min, input_max = min(input_range), max(input_range)
        output_min, output_max = min(output_range), max(output_range)
        output_span = output_max - output_min

        output_values = []
        for input_val in input_values:
            normalized_val = self.normalize(input_val, input_min, input_max)
            output_values.append(normalized_val * output_span + output_min)

        return output_values
