# -*- coding: utf-8 -*-
"""

@author: yang liu

Purpose: BaslerCamera is a wrapper for Basler pypylon, inheriting from PyCamera
to standardize a simple API for integration of cameras into instruments run by a
python framework. part of the code is borrowed from
https://github.com/czbiohub-sf/pyCameras/blob/master/py_cameras/py_basler.py

"""

from copylot.hardware.cameras.abstract_camera import AbstractCamera
from pypylon import pylon
from pypylon import genicam
import sys
from copylot import logger
import numpy as np
from enum import Enum
from time import perf_counter, sleep

exitcode = 0

# ---------------------------------------CONSTANTS-----------------------------------------------
_CAM_TRIG_SLEEP = 0.01
_DEF_START_EXPOSURE_MS = 10
_MAX_CAMLIST_ATTEMPTS = 5


# -----------------------------------------------------------------------------------------------

class BaslerCameraException(Exception):
    pass


def round_to_range(number, lower_bound, upper_bound):
    return min(max(number, lower_bound), upper_bound)


class GrabStrategy(Enum):
    """For more details see https://github.com/basler/pypylon/blob/master/samples/grabstrategies.py

    Additional information available by downloading "Pylon Programmer's Guide and API Reference"
    and searching for "EGrabStrategy".
    """

    ONE_BY_ONE = pylon.GrabStrategy_OneByOne
    LATEST_IMAGE_ONLY = pylon.GrabStrategy_LatestImageOnly
    LATEST_MULTIPLE_IMAGES = pylon.GrabStrategy_LatestImages
    UPCOMING_IMAGE = pylon.GrabStrategy_UpcomingImage


class BaslerCamera(AbstractCamera):

    def __init__(self, camera_index: int = 0):
        self._trigger_mode = 'free_run'
        self._isRunning = False
        self._isActivated = False
        self.camera_index = camera_index
        # get transport layer and all attached devices
        self.tl_factory = pylon.TlFactory.GetInstance()
        self.devices = self.tl_factory.EnumerateDevices()
        self.grab_timeout_ms = 1000*1000
        if len(self.devices) == 0:
            raise pylon.RuntimeException("No camera connected")
        else:
            self.maxCameraToUSe = len(self.devices)
            logger.info(str(self.maxCameraToUSe))
            for device in self.devices:
                logger.info(device.GetFriendlyName())  # return readable name

    def __del__(self):
        self.deactivate_camera()

    def activate_camera(self):
        """Prepares the camera for acquisition.

        The camera device is parameterized with a default configuration
        which sets up free-running continuous acquisition.
        """
        try:
            # Camera set-up
            self.camera = pylon.InstantCamera(self.tl_factory.CreateDevice(self.devices[self.camera_index]))
            logger.info(self.camera.GetDeviceInfo().GetModelName())
            camera_serial = self.camera.DeviceInfo.GetSerialNumber()
            logger.info(f"set context {self.camera_index} for camera {camera_serial}")
            self.SensorWmax = self.camera.SensorWidth.GetValue()
            self.SensorHmax = self.camera.SensorHeight.GetValue()
            self.minWidth = 48
            self.camera.Open()
            if self.camera.IsOpen() is True:
                print(self.camera.SensorReadoutTime.GetValue())
                print(self.camera.ExposureTime.Value)
                self.external_trigger_type_options = self.camera.TriggerSelector.Symbolics
                self.pixel_format_options = self.camera.PixelFormat.Symbolics
                self.exposure_mode_options = self.camera.ExposureMode.Symbolics
                self.trigger_mode_options = self.camera.TriggerMode.Symbolics
                self.acquisition_mode_options = self.camera.AcquisitionMode.Symbolics
                self.trigger_source_options = self.camera.TriggerSource.Symbolics
                self.camera_pixel_bitdepth_options = self.camera.PixelFormat.Symbolics

                # Default configuration is freerun acquisition
                self._isActivated = True
                logger.info(f"{self.camera_index} : Camera activated!")
        except genicam.GenericException as e:
            print("An exception occurred.")
            print(e.GetDescription())

    def deactivate_camera(self):
        if self._isRunning:
            try:
                self.stop_acquisition()
            except Exception as e:
                logger.exception(f"Cam {self.camera_index} : Error stopping acquisition\n{e}")
        self.camera.Close()
        self._isActivated = False
        logger.debug(f"{self.camera_index} : Camera deactivated")

    @property
    def exposure(self):

        return self.camera.ExposureTime.Value

    @exposure.setter
    def exposure(self, value):
        min = self.camera.ExposureTime.Min
        max = self.camera.ExposureTime.Max
        if min <= value <= max:
            self.camera.ExposureTime.SetValue(value)
        else:
            self.camera.ExposureTime.SetValue(value)

    def frame_rate(self):
        return self.camera.AcquisitionFrameRate.Value

    @property
    def image_height(self):
        height = self.camera.Height.Value
        logger.info("SensorMax Height {} for camera".format(height))
        return self.camera.Height.Value

    @image_height.setter
    def image_height(self, value):
        if value % self.minWidth != 0:
            value = int(np.ceil(value / self.minWidth) * self.minWidth)
        self.camera.Height.SetValue(value)

    @property
    def image_width(self):
        width = self.camera.Width.Value
        logger.info("SensorMax Width {} for camera".format(width))
        return self.camera.Width.Value

    @image_width.setter
    def image_width(self, value):
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
        return self.camera.AcquisitionMode.Value

    @acquisition_mode.setter
    def acquisition_mode(self, value):
        if value in self.acquisition_mode_options:
            self.camera.AcquisitionMode.SetValue(value)
        else:
            message = 'pick from ' + self.acquisition_mode_options
            logger.info(message)

    @property
    def binning(self):
        return self.camera.BinningHorizontal.GetValue(), self.camera.BinningVertical.GetValue()

    @binning.setter
    def binning(self, value):
        self.camera.BinningHorizontal.SetValue(value)
        self.camera.BinningVertical.SetValue(value)

    @property
    def exposure_mode(self):
        return self.camera.ExposureMode.Value

    @exposure_mode.setter
    def exposure_mode(self, value):
        if value in self.exposure_mode_options:
            self.camera.ExposureMode.SetValue(value)
        else:
            message = 'pick from ' + self.exposure_mode_options
            logger.info(message)

    @property
    def pixel_format(self):
        return self.camera.PixelFormat.GetValue()

    @pixel_format.setter
    def pixel_format(self, value):
        if value in self.pixel_format_options:
            self.camera.PixelFormat.SetValue(value)
        else:
            message = 'pick from ' + self.pixel_format_options
            logger.info(message)

    @property
    def gain(self):

        return self.camera.Gain.GetValue()

    @gain.setter
    def gain(self, value):
        g_min = self.camera.Gain.GetMin()
        g_max = self.camera.Gain.Gain.GetMax()
        if not g_min <= value <= g_max:
            value = round_to_range(value, g_min, g_max)
        self.camera.Gain.SetValue(value)

    @property
    def external_trigger_type(self):
        return self.camera.TriggerSelector.GetValue()

    @external_trigger_type.setter
    def external_trigger_type(self, value: str):
        if value in self.external_trigger_type_options:
            self.camera.TriggerSelector.SetValue(value)
        else:
            message = 'pick from ' + self.trigger_type_options
            logger.info(message)

    @property
    def trigger(self):
        self.camera.TriggerMode.Value

    @trigger.setter
    def trigger(self, value: str):
        self.camera.TriggerMode.SetValue(value)

    @property
    def trigger_source(self):
        return self.camera.TriggerSource.Value

    @trigger_source.setter
    def trigger_source(self, value):
        if value in self.trigger_source_options:
            self.camera.TriggerSource.SetValue(value)
        else:
            message = 'pick from ' + self.trigger_source_options
            logger.info(message)

    @property
    def camera_pixel_bitdepth(self):
        return self.camera.PixelFormat.Value

    @camera_pixel_bitdepth.setter
    def camera_pixel_bitdepth(self, value):
        if value in self.camera.PixelFormat.Symbolics:
            self.camera.PixelFormat.SetValue(value)
        else:
            message = 'pick from ' + self.PixelFormat.Symbolics
            logger.info(message)

    def reset_camera(self):
        self.camera.DeviceReset.Execute()

    def software_trigger(self):
        self.camera.ExecuteSoftwareTrigger()

    def config_trigger(self, t_type='free_run'):
        trig_type = ['free_run', 'software', 'hardware']
        if t_type is not None:
            if t_type in trig_type:
                self.camera.AcquisitionMode.SetValue('Continuous')
                if t_type != 'free_run':
                    self.trigger = 'On'
                    if t_type == 'software':
                        self.trigger_source = 'Software'
                        self.camera.RegisterConfiguration(
                            pylon.SoftwareTriggerConfiguration(),
                            pylon.RegistrationMode_ReplaceAll,
                            pylon.Cleanup_Delete,
                        )
                    elif t_type == "hardware":
                        self.trigger_source = 'Line 1'
                        self.camera.RegisterConfiguration(
                            pylon.HardwareTriggerConfiguration(),
                            pylon.RegistrationMode_ReplaceAll,
                            pylon.Cleanup_Delete,
                        )
                else:
                    self.trigger = 'Off'
                    self._trigger_mode = t_type
            else:
                logger.info('Please select from the options' + trig_type)
        else:
            self.camera.AcquisitionMode.SetValue('Continuous')
            self.camera.TriggerMode.SetValue('Off')
            self._trigger_mode = t_type
        logger.info(f"Cam {self.camera_index} : Trigger is set")

    def convertTo_uint16(self, img):
        # This function converts the provided numpy array, img, into uint16 format.
        # The image pixel values are scaled to the uint16 range [0,65535].
        minVal = img.min().astype("float")
        maxVal = img.max().astype("float")

        # Scale image
        img = np.uint16(65535 * (img.astype("float") - minVal) / (maxVal - minVal))

        return img

    def snap(self):
        """
        If the camera is running, returns a numpy array containing the image data from the camera.

        Note that this function does NOT check if the trigger is ready (https://docs.baslerweb.com/acquisition-status) since not all
        Basler camera models support that feature. It is up to caller to protect against overtriggering.
        """
        logger.info(f"Cam {self.camera_index} : snapImage with trigger mode {self._trigger_mode}")
        if self._isRunning:
            if self._trigger_mode == "software":
                for i in range(_MAX_CAMLIST_ATTEMPTS):
                    try:
                        logger.debug(f"Cam {self.camera_index} : Executing software trigger")
                        self.camera.software_trigger()
                        sleep(_CAM_TRIG_SLEEP)
                        grabResult = self.camera.RetrieveResult(
                            self.grab_timeout_ms, pylon.TimeoutHandling_ThrowException
                        )
                        if grabResult and grabResult.GrabSucceeded():
                            logger.debug(f"Cam {self.camera_index} : Grab succeeded!")
                            img = grabResult.GetArray()
                            grabResult.Release()
                            return img
                        else:
                            if grabResult.GetErrorCode() == 3774873620:
                                logger.debug(
                                    f"Cam {self.camera_index} : Packets dropped while acquiring on attempt {i + 1}. There are {_MAX_CAMLIST_ATTEMPTS - i - 1} attempts left. Retrying..."
                                )
                            else:
                                raise RuntimeError(
                                    f"Encountered error grabbing image: grabResult Error code is {grabResult.GetErrorCode()}"
                                )
                    except Exception as e:
                        logger.exception(e)

            elif self._trigger_mode == "free_run":
                logger.debug(f"{self.camera_index} : Freerun image grab.")
                grabResult = self.camera.RetrieveResult(
                    self.grab_timeout_ms, pylon.TimeoutHandling_ThrowException
                )
                if grabResult and grabResult.GrabSucceeded():
                    img = grabResult.GetArray()
                    grabResult.Release()
                    return img
            logger.exception(
                f"self._triggerMode is not valid: needs to be one of free_run, software, got {self._trigger_mode}"
            )
            raise RuntimeError(
                f"self._triggerMode is not valid: needs to be one of free_run, software, got {self._trigger_mode}"
            )
        else:
            logger.exception(
                f"Cam {self.camera_index} : Error: Start acquisition before snapping image."
            )
            raise RuntimeError(
                f"{self.camera_index} : Error: Start acquisition before snapping image."
            )

    def start_acquisition(self, grabStrategy: GrabStrategy):
        """Sets up acquisition and begins grabbing images.

        Note this function does not implement either hardware or software trigger
        "wait" functions (for more details see https://docs.baslerweb.com/line-source#trigger-wait).
        This is because not all Basler camera models implement the feature necessary to check
        if the device is ready to receive a trigger signal. For example, for the ULCMM camera
        (daA1600-60um), the AcquisitionStatus function is unavailable and thus cannot be used
        to check when the camera is ready to receive another software signal.
        """
        if not self._isRunning:
            try:
                self.camera.AcquisitionMode.SetValue("Continuous")
                self._isRunning = True

                # Grab strategy must be in place before executing acquisition start
                self.camera.StartGrabbing(grabStrategy.value)
                self.camera.AcquisitionStart.Execute()
                logger.debug(
                    f"Starting acquisition with trigger mode {self._trigger_mode}"
                )
            except Exception as e:
                logger.exception(e)

    def stop_acquisition(self):
        try:
            self.camera.AcquisitionStop.Execute()
            self.camera.StopGrabbing()
            self._isRunning = False
            logger.debug(f"Cam {self.camera_index}: Ended acquisition")
        except Exception as e:
            logger.exception(f"Cam {self.camera_index}: error in stopAcquisition")

    def trigger_ready(self):
        """Not all Basler cameras have the AcquisitionStatus function.

        For those without, it is up to the caller to deal with the possibility of overtriggeirng/dropped frames.
        For more detail, see: https://docs.baslerweb.com/overlapping-image-acquisition#avoiding-overtriggering
        """

        try:
            isWaitingForAcqStart = self.camera.AcquisitionStatus.Value
            return isWaitingForAcqStart
        except:
            logger.exception(
                f"Cam {self.camera_index} : Error attempting to check AcquisitionStatus.GetValue()"
            )

    def get_img(self, grabStrategy: GrabStrategy):
        """Returns a generator of images as numpy arrays as the camera is grabbing images.

        You can iterate through these images by:

            for img in camera.yieldImages():
                do stuff
        or
            img_generator = camera.yieldImages()
            get_next_image, timestamp_s = next(img_generator)

        Returns
        -------
        Tuple[np.ndarray, int]
            The image (numpy array) and the timestamp (int) of when it was acquired
        """

        if not self._isRunning:
            self.start_acquisition(grabStrategy)
        while self.camera.IsGrabbing():
            grabResult = self.camera.RetrieveResult(
                self.grab_timeout_ms, pylon.TimeoutHandling_ThrowException
            )
            if grabResult and grabResult.GrabSucceeded():
                timestamp = perf_counter()
                yield grabResult.Array, timestamp
                grabResult.Release()

        return grabResult.Array
    # --------------------------------------------------------------------------------------------------
