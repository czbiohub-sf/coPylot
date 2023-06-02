from pypylon import pylon
from pypylon import genicam
import sys

exitcode = 0


class bCam:
    def __init__(self):
        # get transport layer and all attached devices
        self.cameras = None
        self.tl_factory = pylon.TlFactory.GetInstance()
        self.devices = self.tl_factory.EnumerateDevices()
        if len(self.devices) == 0:
            raise pylon.RuntimeException("No camera connected")
        else:
            self.maxCameraToUSe = len(self.devices)
            print(len(self.maxCameraToUSe))
            for device in self.devices:
                print(device.GetFriendlyName())  # return readable name

    def __del__(self):
        self.closecam()
        exitcode = 1
        sys.exit(exitcode)

    def opencam(self):
        try:
            self.cameras = pylon.InstantCameraArray(min(len(self.devices)),
                                                    self.maxCameraToUSe)  # create multiple camera
            # Create and attach all Pylon Devices.
            for i, cam in enumerate(self.cameras):
                cam.Attach(self.tlFactory.CreateDevice(self.devices[i]))
                cam.Open()
                # Print the model name of the camera.
                print("Using device ", cam.GetDeviceInfo().GetModelName())
        except genicam.GenericException as e:
            # Error handling
            print("An exception occurred. {}".format(e))
            exitcode = 1
            sys.exit(exitcode)
    def closecam(self):
        for i, cam in enumerate(self.cameras):
            cam.Close()
    def trigermode(self,cam):
        cam.Attach(AcquisitionMode.SetValue(AcquisitionMode_SingleFrame);
)


