from pyvcam import pvc
from pyvcam.camera import Camera


class PrimeBSICamera:
    def __init__(
            self,
            scan_mode,
            binning: tuple,
    ):
        pvc.init_pvcam()

        self.cam.prog_scan_mode = scan_mode
        self.cam.binning = binning

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
    def gain(self):
        return self.cam.gain

    @gain.setter
    def gain(self, gain):
        self.cam.gain = gain

    @binning.setter
    def binning(self, x_bin, y_bin):
        """
        Binning property setter. If you want to set
        square binning, you should pass equal values
        for x_bin and y_bin.

        Parameters
        ----------
        x_bin
        y_bin

        """
        self.cam.binning = (x_bin, y_bin)

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
