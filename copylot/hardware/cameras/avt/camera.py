import sys
from enum import Enum
from typing import Tuple

from copylot.hardware.cameras.abstract_camera import AbstractCamera
from copylot.hardware.cameras.avt.vimba import Vimba


class BinningMode(Enum):
    AVERAGE = "Average"
    SUM = "Sum"


class AVTCameraException(Exception):
    pass


class AVTCamera(AbstractCamera):
    def __init__(self, nb_camera = 1):
        self.nb_camera = nb_camera

        self._exposure_time = None

        # Internal variables used to keep track of the number of
        # > total images
        # > incomplete frames
        # > frames dropped (i.e the caller attempted to get an image but none were in the queue),
        # > times a frame was attempted to be placed in the queue but failed because the queue was full
        self.all_count = 0
        self.incomplete_count = 0
        self.dropped_count = 0
        self.full_count = 0

        self._isActivated = False
        # self.queue: queue.Queue[Tuple[np.ndarray, float]] = queue.Queue(maxsize=1)

    @property
    def temperature(self) -> float:
        """Get the device temperature

        Returns
        -------
        float

        """
        try:
            return self.camera.DeviceTemperature.get()
        except Exception as e:
            self.logger.error(
                f"Could not get the device temperature using DeviceTemperature: {e}"
            )
            raise e

    @property
    def exposure_bounds(self):
        try:
            exposure_bounds = []
            with Vimba.get_instance() as vimba:
                for cam in vimba.get_all_cameras():
                    with cam:
                        exposure_bounds.append(
                            (
                                cam.ExposureAutoMin.get() / 1000,
                                cam.ExposureAutoMax.get() / 1000
                            )
                        )
            return exposure_bounds
        except Exception as e:
            self.logger.error(
                f"Could not get exposure using ExposureAutoMin / ExposureAutoMax: {e}"
            )
            raise e

    @property
    def exposure_time(self):
        return self._exposure_time

    @exposure_time.setter
    def exposure_time(self, cam_index_and_value: Tuple[int, int]):
        camera_index, value = cam_index_and_value
        min_exposure, max_exposure = self.exposure_bounds[camera_index]
        if min_exposure <= value <= max_exposure:
            try:
                with Vimba.get_instance() as vimba:
                    camera = vimba.get_all_cameras()[camera_index]
                    camera.ExposureTime.set(value * 1000)

                    self._exposure_time = camera.ExposureTime.get() / 1000

                print(f"Exposure time set to {self.exposure_time} ms.")
            except Exception as e:
                print(f"Failed to set exposure: {e}")
                raise e
        else:
            raise ValueError(
                f"value out of range: must be in "
                f"[{min_exposure}, {max_exposure}], but value_ms={value}"
            )

    @staticmethod
    def acquire_single_frame():
        with Vimba.get_instance() as vimba:
            cams = vimba.get_all_cameras()
            with cams[0] as cam:
                # Aquire single frame synchronously
                frame = cam.get_frame()

        return frame

    # def start_acquisition(self):
    #     with Vimba.get_instance() as vimba:
    #         cams = vimba.get_all_cameras()
    #         if self.nb_camera == 1:
    #             with cams[0] as cam:

