from dataclasses import dataclass
from re import T
from copylot.hardware.cameras.abstract_camera import AbstractCamera
from copylot.hardware.mirrors.abstract_mirror import AbstractMirror
from copylot.hardware.lasers.abstract_laser import AbstractLaser
from copylot.hardware.stages.abstract_stage import AbstractStage
from copylot.hardware.daqs.abstract_daq import AbstractDAQ
from copylot.assemblies.photom.utils.affine_transform import AffineTransform
from copylot.assemblies.photom.utils.scanning_algorithms import (
    calculate_rectangle_corners,
)
from pathlib import Path
from copylot import logger
from typing import Tuple
import time
from typing import Optional

# TODO: add the logger from copylot


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

        self._calibrating = False

        # TODO: replace these hardcoded values to mirror's scan steps given the magnification
        # and the mirrors angles
        self._calibration_rectangle_size_xy = [0.004, 0.004]

        assert len(self.mirror) == len(affine_matrix_path)

        # Apply AffineTransform to each mirror
        for i, tx_path in enumerate(affine_matrix_path):
            self.mirror[i].affine_transform_obj = AffineTransform(config_file=tx_path)

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

    def stop_mirror(self, mirror_index: int):
        if mirror_index < len(self.mirror):
            self._calibrating = False
        else:
            raise IndexError("Mirror index out of range.")

    # TODO probably will replace the camera with zyx or yx image array input
    ## Camera Functions
    def capture(self):
        pass

    ## Mirror Functions
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

    def get_sensor_size(self):
        if self.camera is not None:
            self.camera_sensor_size = self.camera[0].sensor_size
        else:
            raise NotImplementedError("No camera found.")
