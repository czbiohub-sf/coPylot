from copylot.hardware.cameras.abstract_camera import AbstractCamera
from pypylon import pylon as py
from pypylon import genicam
import sys

exitcode = 0


class OrcaCameraException(Exception):
    pass


class BaslerCamera(AbstractCamera):
    def __init__(self):
        # get transport layer and all attached devices
        self.camera = None
        self.tl_factory = py.TlFactory.GetInstance()
        self.devices = self.tl_factory.EnumerateDevices()
        if len(self.devices) == 0:
            raise py.RuntimeException("No camera connected")
        else:
            self.maxCameraToUSe = len(self.devices)
            print(self.maxCameraToUSe)
            for device in self.devices:
                print(device.GetFriendlyName())  # return readable name

    def __del__(self):
        self.closecam()

    def opencam(self, camnum=None):
        try:
            if len(self.devices) < 2:
                self.camera = py.InstantCamera(self.tl_factory.CreateFirstDevice())
            else:
                if camnum is not None:
                    self.camera = py.InstantCamera(
                        self.tl_factory.CreateDevice(self.devices[camnum]))  # create multiple camera
                else:
                    self.camera = py.InstantCamera(self.tl_factory.CreateDevice(self.devices[0]))
            print("Using device ", self.camera.GetDeviceInfo().GetModelName())
            camera_serial = self.camera.DeviceInfo.GetSerialNumber()
            print(f"set context {camnum} for camera {camera_serial}")
            self.SensorWmax = self.camera.SensorWidth.GetValue()
            self.SensorHmax = self.camera.SensorHeight.GetValue()
            self.camera.Open()
            if self.camera.IsOpen() is True:
                self.camera.SensorReadoutTime.GetValue()
                self.camera.ExposureTime.GetValue()
        except genicam.GenericException as e:
            # Error handling
            print("An exception occurred. {}".format(e))
            exitcode = 1
            sys.exit(exitcode)



    def closecam(self):
        try:
            # Check whether there is any camera(s) are running and stop the running cam
            if self.camera.AcquisitionStatus.GetValue() is True:
                self.camera.AcquisitionAbort.Execute()
            # close cam
            self.camera.Close()

        except genicam.GenericException as e:
            # Error handling
            print("An exception occurred. {}".format(e))
            exitcode = 1
            sys.exit(exitcode)

    @property
    def exposure(self):

        return self.camera.ExposureTime.GetValue()

    @exposure.setter
    def set_exposure(self, value):
        if value is not None:
            value = self.camera.ExposureTime.GetMin()
        self.camera.ExposureTime.SetValue(value)

    @property
    def image_height(self):
        height = self.camera.Height.GetValue()
        print("SensorMax Height {} for camera".format(height))
        return height

    @image_height.setter
    def set_image_height(self, value):
        self.camera.Height.SetValue(value)

    @property
    def image_width(self):
        width = self.camera.Width.GetValue()
        print("SensorMax Width {} for camera".format(width))
        return width

    @image_width.setter
    def set_image_width(self, value):
        self.camera.Width.SetValue(value)

    def imagesize(self):
        '''

        Returns
        -------
        Size(Height,Width): int
                        retun the currnet image size
        '''

        return self.image_width(), self.image_height()

    def aliviable_acqMode(self):
        '''

        Returns
        -------
        string:
         This will return available Acquisition mode that the camera has
        '''
        return self.camera.AcquisitionMode.GetSymbolics()

    @property
    def acq_mode(self):
        '''

        Parameters
        ----------
        camnum:int
            set the camera number and the default would be camera 0

        Returns
        -------
            value:string
                current status of the AcquisitionsMode
        '''
        value = self.camera.AcquisitionMode.GetValue()
        return value

    @acq_mode.setter
    def acq_mode(self, value):
        if value is not None:
            self.camera.AcquisitionMode.SetValue(value)
