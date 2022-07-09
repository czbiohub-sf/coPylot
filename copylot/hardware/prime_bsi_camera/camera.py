from pyvcam import pvc, constants
from pyvcam.camera import Camera


class PrimeBSICamera:
    def __init__(
        self,
        camera_name: str = None,
        # TODO: create properties for these
        # scan_mode: str = None,
        # scan_dir: str = None,
        # binning: tuple = (1, 1),
        # trigger_mode: str = None,
        # exposure_out: str = None,
        enable_metadata: bool = True,
    ):
        """

        Parameters
        ----------
        camera_name : str
            Camera name, available through available_cameras().
            If not provided, the next available camera will be initialized.
        enable_metadata : bool
            Toggles camera metadata on and off. By default, it is True.
        """
        pvc.init_pvcam()

        if camera_name:
            try:
                self.cam = Camera.select_camera(camera_name)
            except:
                pvc.uninit_pvcam()
                raise
        else:
            try:
                self.cam = next(Camera.detect_camera())
            except:
                pvc.uninit_pvcam()
                raise

        self.cam.open()

        # Prime BSI Express camera has only one port called 'CMOS' at index 0
        self.cam.readout_port = 0

        # Hard-coding these values since they won't change
        # Values can be parsed from self.cam.port_speed_gain_table['CMOS']
        self._speed_gain_table = {'200 MHz': {'speed_index': 0,
                                              'Full well': {'gain_index': 1, 'bit_depth': 11},
                                              'Balanced': {'gain_index': 2, 'bit_depth': 11},
                                              'Sensitivity': {'gain_index': 3, 'bit_depth': 11}
                                              },
                                  '100 MHz': {'speed_index': 1,
                                              'HRD': {'gain_index': 1, 'bit_depth': 16},
                                              'CMS': {'gain_index': 1, 'bit_depth': 12}
                                              }
                                  }

        self.serial_number = self.cam.serial_no
        self.sensor_size = self.cam.sensor_size
        self.chip_name = self.cam.chip_name
        self.cam.meta_data_enabled = enable_metadata

    def __del__(self):
        self.cam.finish()
        self.cam.close()
        pvc.uninit_pvcam()

    @staticmethod
    def available_cameras():
        pvc.init_pvcam()
        cameras = Camera.get_available_camera_names()

        pvc.uninit_pvcam()
        return cameras

    @property
    def speed_gain_table(self):
        return self._speed_gain_table

    # Will implement later
    # def available_scan_modes(self):
    #     scan_modes = self.cam.__prog_scan_modes
    #
    #     print(f"Available scan modes: {scan_modes}")
    #
    #     return scan_modes

    @property
    def exposure_time(self):
        return self.cam.exp_time

    @exposure_time.setter
    def exposure_time(self, exposure_time):
        self.cam.exp_time = exposure_time

    @property
    def readout_speed(self):
        readout_speed_name = None

        readout_speed_index = self.cam.speed_table_index
        for key, value in self.speed_gain_table.items():
            if value['speed_index'] == readout_speed_index:
                readout_speed_name = key

        return readout_speed_name

    @readout_speed.setter
    def readout_speed(self, new_speed):
        success = False

        for key, value in self.speed_gain_table.items():
            if key == new_speed:
                success = True
                self.cam.speed_table_index = value['speed_index']

        if not success:
            raise ValueError('Invalid readout speed. '
                             'Please check speed_gain_table for valid settings.')

    @property
    def gain(self):
        gain_name = None

        for key, value in self.speed_gain_table[self.readout_speed].items():
            if isinstance(value, dict):
                if value['gain_index'] == self.cam.gain:
                    gain_name = key

        return gain_name

    @gain.setter
    def gain(self, gain):
        success = False

        for key, value in self.speed_gain_table[self.readout_speed].items():
            if key == gain:
                success = True
                self.cam.gain = value['gain_index']

        if not success:
            raise ValueError('Invalid gain. '
                             'Please check speed_gain_table for valid settings.')

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
