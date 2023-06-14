from copylot.hardware.cameras.abstract_camera import AbstractCamera
from pypylon import pylon as py
from pypylon import genicam
import sys
from copylot import logger
import numpy as np
from pdb import set_trace as st

exitcode = 0


class BaslerCameraException(Exception):
    pass


def round_to_range(number, lower_bound, upper_bound):
    return min(max(number, lower_bound), upper_bound)


class BaslerCamera(AbstractCamera):

    def __init__(self, camera_index: int = 0):
        self.trigger_type_options = None
        self.acquisition_mode_options = None
        self.trigger_mode_options = None
        self.exposure_mode_options = None
        self.pixel_format_options = None
        self.minWidth = None
        self.SensorHmax = None
        self.SensorWmax = None
        self._trigger_selector = None
        self.camera_index = camera_index
        # get transport layer and all attached devices
        self.camera = None
        self.tl_factory = py.TlFactory.GetInstance()
        self.devices = self.tl_factory.EnumerateDevices()
        if len(self.devices) == 0:
            raise py.RuntimeException("No camera connected")
        else:
            self.maxCameraToUSe = len(self.devices)
            logger.info(str(self.maxCameraToUSe))
            for device in self.devices:
                logger.info(device.GetFriendlyName())  # return readable name

    def __del__(self):
        self.closecam()

    def opencam(self):
        try:
            if len(self.devices) < 2:
                self.camera = py.InstantCamera(self.tl_factory.CreateFirstDevice())
            else:
                if self.camera_index != 0:
                    self.camera = py.InstantCamera(
                        self.tl_factory.CreateDevice(self.devices[self.camera_index]))  # create multiple camera
                else:
                    self.camera = py.InstantCamera(self.tl_factory.CreateDevice(self.devices[self.camera_index]))
            logger.info(self.camera.GetDeviceInfo().GetModelName())
            camera_serial = self.camera.DeviceInfo.GetSerialNumber()
            logger.info(f"set context {self.camera_index} for camera {camera_serial}")
            self.SensorWmax = self.camera.SensorWidth.GetValue()
            self.SensorHmax = self.camera.SensorHeight.GetValue()
            self.minWidth = 48
            self.camera.Open()
            if self.camera.IsOpen() is True:
                print(self.camera.SensorReadoutTime.GetValue())
                print(self.camera.ExposureTime.GetValue())
                self.trigger_type_options = self.camera.TriggerSelector.GetSymbolics()
                self.pixel_format_options = self.camera.PixelFormat.GetSymbolics()
                self.exposure_mode_options = self.camera.ExposureMode.GetSymbolics()
                self.trigger_mode_options = self.camera.TriggerMode.GetSymbolics()
                self.acquisition_mode_options = self.camera.AcquisitionMode.GetSymbolics()
        except genicam.GenericException as e:
            # Error handling
            logger.info("An exception occurred. {}".format(e))
            exitcode = 1
            sys.exit(exitcode)

    def closecam(self):
        try:
            # close cam
            self.camera.Close()

        except genicam.GenericException as e:
            # Error handling
            logger.info("An exception occurred. {}".format(e))
            exitcode = 1
            sys.exit(exitcode)

    @property
    def exposure(self):

        return self.camera.ExposureTime.GetValue()

    @exposure.setter
    def exposure(self, value):
        if value is not None:
            value = self.camera.ExposureTime.GetMin()
        self.camera.ExposureTime.SetValue(value)

    def frame_rate(self):
        return self.camera.AcquisitionFrameRate.GetValue()

    @property
    def image_height(self):
        height = self.camera.Height.GetValue()
        logger.info("SensorMax Height {} for camera".format(height))
        return self.camera.Height.GetValue()

    @image_height.setter
    def image_height(self, value: int):
        if value % self.minWidth != 0:
            value = int(np.ceil(value / self.minWidth) * self.minWidth)
        self.camera.Height.SetValue(value)

    @property
    def image_width(self):
        width = self.camera.Width.GetValue()
        logger.info("SensorMax Width {} for camera".format(width))
        return self.camera.Width.GetValue()

    @image_width.setter
    def image_width(self, value: int):
        """

        Parameters
        ----------
        value

        Returns
        -------

        """
        if value % self.minWidth != 0:
            value = int(np.ceil(value / self.minWidth) * self.minWidth)
        self.camera.Width.SetValue(value)

    def imagesize(self):
        """

        Returns
        -------
        Size(Height,Width): int
                        retun the currnet image size
        """

        return self.image_width, self.image_height

    @property
    def acquisition_mode(self):
        '''

        Parameters
        ----------
        :int
            set the camera number and the default would be camera 0

        Returns
        -------
            value:string
                current status of the AcquisitionsMode
        '''
        return self.camera.AcquisitionMode.GetValue()

    @acquisition_mode.setter
    def acquisition_mode(self, value: str):
        if value in self.acquisition_mode_options:
            self.camera.AcquisitionMode.SetValue(value)
        else:
            message = 'pick from '+self.acquisition_mode_options
            logger.info(message)

    @property
    def binning(self):
        return self.camera.BinningHorizontal.GetValue(), self.camera.BinningVertical.GetValue()

    @binning.setter
    def binning(self, value: int):
        self.camera.BinningHorizontal.SetValue(value)
        self.camera.BinningVertical.SetValue(value)

    def acquisition_start(self):
        self.camera.AcquisitionStart.Execute()

    def acquisition_stop(self):
        self.camera.AcquisitionStop.Execute()

    @property
    def exposure_mode(self):
        return self.camera.ExposureMode.GetValue()

    @exposure_mode.setter
    def exposure_mode(self, value: str):
        if value in self.exposure_mode_options:
            self.camera.ExposureMode.SetValue(value)
        else:
            message = 'pick from '+self.exposure_mode_options
            logger.info(message)


    @property
    def pixel_format(self):
        return self.camera.PixelFormat.GetValue()

    @pixel_format.setter
    def pixel_format(self, value: str):
        if value in self.pixel_format_options:
            self.camera.PixelFormat.SetValue(value)
        else:
            message = 'pick from '+self.pixel_format_options
            logger.info(message)

    @property
    def gain(self):

        return self.camera.Gain.GetValue()

    @gain.setter
    def gain(self, value: float):
        g_min = self.camera.Gain.GetMin()
        g_max = self.camera.Gain.Gain.GetMax()
        if not g_min <= value <= g_max:
            value = round_to_range(value, g_min, g_max)
        self.camera.Gain.SetValue(value)

    @property
    def trigger_selector(self):
        return self.camera.TriggerSelector.GetValue()

    @trigger_selector.setter
    def trigger_selector(self, value: str):
        if value in self.trigger_type_options:
            self.camera.TriggerSelector.SetValue(value)
        else:
            message = 'pick from '+self.trigger_type_options
            logger.info(message)

    @property
    def trigger_mode(self):
        self.camera.TriggerMode.GetValue()

    @trigger_mode.setter
    def trigger_mode(self, value: bool):
        if value in self.trigger_mode_options:
            self.camera.TriggerMode.SetValue(value)
        else:
            message = 'pick from '+self.trigger_mode_options
            logger.info(message)

