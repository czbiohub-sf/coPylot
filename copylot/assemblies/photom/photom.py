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
        self._calibration_rectangle_size_xy = [0.002, 0.002]

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
