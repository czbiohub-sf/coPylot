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
        exitcode = 1
        sys.exit(exitcode)

    def opencam(self,camnum=None):
        try:
            if len(self.devices)<2:
                self.camera = py.InstantCamera(self.tl_factory.CreateFirstDevice())
            else:
                if camnum is not None:
                    self.camera = py.InstantCamera(self.tl_factory.CreateDevice(self.devices[camnum]))  # create multiple camera
                else:
                    self.camera = py.InstantCamera(self.tl_factory.CreateDevice(self.devices[0]))
            print("Using device ", self.camera.GetDeviceInfo().GetModelName())
            camera_serial = self.camera.DeviceInfo.GetSerialNumber()
            print(f"set context {camnum} for camera {camera_serial}")
            self.SensorWmax = self.camera.WidthMax.GetValue()
            self.SensorHmax = self.camera.HeightMax.GetValue()
            self.camera.Open()
            self.is_open()
        except genicam.GenericException as e:
            # Error handling
            print("An exception occurred. {}".format(e))
            exitcode = 1
            sys.exit(exitcode)
    @property
    def is_open(self):
        '''

        Returns
        -------

        '''

        return self.camera.IsOpen()
    def closecam(self):
        try:
            # Check whether there is any camera(s) are running and stop the running cam
            if self.camera.isGrabbing():
                for idx, cam in enumerate(self.camera):
                    cam.AcquisitionAbort.Execute()
            #close cam
            self.camera.Close()

        except genicam.GenericException as e:
            # Error handling
            print("An exception occurred. {}".format(e))
            exitcode = 1
            sys.exit(exitcode)

    @property
    def image_height(self):
        height = self.camera.Height.GetValue()
        print("SensorMax Height {} for camera".format(height))
        return height
    @property.setter
    def image_height(self,value=None):
        if value is not None:
            self.camera.Height.SetValue(value)
        else:
            self.camera.Height.SetValue(self.SensorHmax)
    @property
    def image_width(self):
        width = self.camera.Width.GetValue()
        print("SensorMax Width {} for camera".format(width))
        return width

    @property.setter
    def image_width(self,value=None):
        if value is not None:
            self.camera.Width.SetValue(value)
        else:
            self.camera.Width.SetValue(self.SensorWmax)

    @property
    def imagesize(self):
        '''

        Returns
        -------
        Size(Height,Width): int
                        retun the currnet image size
        '''

        return self.image_width(),self.image_height()


    def aliviable_acqMode(self):
        '''

        Returns
        -------
        string:
         This will return available Acquisition mode that the camera has
        '''
        return self.cameras[0].AcquisitionMode.GetSymbolics()

    @property
    def acqMode(self):
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

    @acqMode.setter
    def acqMode(self,value=None):
        if value is not None:
            self.camera.AcquisitionMode.SetValue(value)