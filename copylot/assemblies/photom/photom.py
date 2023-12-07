from dataclasses import dataclass
from re import T
from copylot.hardware.cameras.abstract_camera import AbstractCamera
from copylot.hardware.mirrors.abstract_mirror import AbstractMirror
from copylot.hardware.lasers.abstract_laser import AbstractLaser
from copylot.hardware.stages.abstract_stage import AbstractStage
from copylot.hardware.daqs.abstract_daq import AbstractDAQ
from copylot.assemblies.photom.utils.affine_transform import AffineTransform
from pathlib import Path
from copylot import logger
from typing import Tuple

class PhotomAssembly:
    def __init__(
        self,
        laser: list[AbstractLaser],
        mirror: list[AbstractMirror],
        affine_matrix_path: list[Path],
        camera: list[AbstractCamera] = None,
        dac: list[AbstractDAQ] = None,
    ):
        # hardware
        self.camera = camera
        self.laser = laser  # list of lasers
        self.mirror = mirror
        self.DAC = dac

        assert len(self.mirror) == len(affine_matrix_path)

        # Apply AffineTransform to each mirror
        for i, tx_path in enumerate(affine_matrix_path):
            self.mirror[i].affine_transform_obj = AffineTransform(config_file=tx_path)

    def calibrate(self, mirror_index: int):
        if mirror_index < len(self.mirror):
            # Logic for calibrating the mirror
            pass
            # moving the mirror in a rectangle
        else:
            raise IndexError("Mirror index out of range.")

    # TODO probably will replace the camera with zyx or yx image array input
    ## Camera Functions
    def capture(self):
        pass

    ## Mirror Functions
    def get_position(self, mirror_index: int)->list[float, float]:
        if mirror_index < len(self.mirror):
            if self.DAC is None:
                NotImplementedError("No DAC found.")
            else:
                return list(self.mirror[mirror_index].position)
        else:
            raise IndexError("Mirror index out of range.")

    def set_position(self, mirror_index: int, position: list[float]):
        if mirror_index < len(self.mirror):
            if self.DAC is None:
                NotImplementedError("No DAC found.")
            else:
                # TODO: logic for applying the affine transform to the position
                new_position = self.mirror.affine_transform_obj.apply_affine(position)
                self.mirror[mirror_index].position = new_position
        else:
            raise IndexError("Mirror index out of range.")

    ## LASER Fuctions
    def get_laser_power(self, laser_index: int, power: float):
        return self.laser[laser_index].power

    def set_laser_power(self, laser_index: int, power: float):
        self.laser[laser_index].power = power
