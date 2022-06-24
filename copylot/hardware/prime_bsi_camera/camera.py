from pyvcam import pvc
from pyvcam.camera import Camera


class PrimeBSICamera:
    def __init__(
            self,
            scan_mode,
            scan_dir,
            binning: tuple,
            enable_metadata: bool = True,
    ):
        """

        Parameters
        ----------
        scan_mode
        binning : tuple
            (x_bin, y_bin). If you want to set square
            binning, you should pass equal values for
            x_bin and y_bin.
        """
        pvc.init_pvcam()

        self.cam.prog_scan_mode = scan_mode
        self.cam.prog_scan_dir = scan_dir
        self.cam.binning = binning

        self.cam.set_param(constants.PARAM_METADATA_ENABLED, enable_metadata)

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

    @property
    def exposure_time(self):
        return self.cam.exp_time

    @exposure_time.setter
    def exposure_time(self, exposure_time):
        self.cam.exp_time = exposure_time

    def reset_rois(self):
        """Restores ROI to the default."""
        self.cam.reset_rois()

    def set_roi(self, s1: int, p1: int, width: int, height: int):
        """
        Adds a new ROI with given parameters to the list of ROIs.

        Parameters
        ----------
        s1 : int
            Serial coordinate of the first corner
        p1 : int
            Parallel coordinate of the first corner
        width : int
            Width of ROI in number of pixels
        height : int
            Height of ROI in number of pixels

        """
        self.cam.set_roi(s1, p1, width, height)

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
