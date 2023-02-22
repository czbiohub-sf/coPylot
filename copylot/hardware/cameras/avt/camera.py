import sys
from enum import Enum

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

    def acquire_single_frame(self):
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

