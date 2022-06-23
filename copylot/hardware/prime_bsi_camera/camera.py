from pyvcam import pvc
from pyvcam.camera import Camera


class PrimeBSICamera:
    def __init__(self):
        pvc.init_pvcam()

    def __del__(self):
        pvc.uninit_pvcam()

    @staticmethod
    def available_cameras():
        cameras = Camera.get_available_camera_names()
        print(f"Available cameras: {cameras}")

        return cameras

    @staticmethod
    def available_scan_modes():
        cam = next(Camera.detect_camera())
        scan_modes = cam.__prog_scan_modes

        print(f"Available scan modes: {scan_modes}")

        return scan_modes

    @property
    def scan_mode(self):
        return self.cam.prog_scan_mode

    @scan_mode.setter
    def scan_mode(self, scan_mode):
        self.cam.prog_scan_mode = scan_mode

    def live_run(self, exposure: int = 20):
        """
        Live mode run method.

        Parameters
        ----------
        exposure : int

        Returns
        -------

        """
        self.cam.start_live(exposure)

        return self.cam.poll_frame
