from enum import Enum

from copylot.hardware.cameras.abstract_camera import AbstractCamera
from copylot.hardware.cameras.avt.vimba import Vimba


class BinningMode(Enum):
    AVERAGE = "Average"
    SUM = "Sum"


class AVTCameraException(Exception):
    pass


class AVTCamera(AbstractCamera):
    def __init__(self):
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
        self.vimba = Vimba.get_instance().__enter__()
        self.queue: queue.Queue[Tuple[np.ndarray, float]] = queue.Queue(maxsize=1)
        self.connect()

    def __del__(self):
        """Cleanup - however best not to rely on __del__."""
        self.deactivateCamera()

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

    def connect(self):
        """Get and connect to the camera using an explicit __enter__ (circumvent the context manager)
        and set default camera settings.
        """
        self.camera = self._get_camera()
        self.camera.__enter__()
        self._camera_setup()
        self._isActivated = True

