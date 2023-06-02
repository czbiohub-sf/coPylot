from pypylon import pylon
from pypylon import genicam
import sys

exitCode=0
class bCam:

    def __init__(self):
        # get transport layer and all attached devices
        self.tl_factory = pylon.TlFactory.GetInstance()
        self.devices = tl_factory.EnumerateDevices()
        if len(self.devices) == 0:
            raise pylon.RuntimeException("No camera connected")
        else:
            self.maxCameraToUSe = len(self.devices)
            print(len(self.maxCameraToUSe))
            for device in self.devices:
                print(device.GetFriendlyName())  # return readable name

    def __del__(self):


    def openCam(self):
        try:
            self.cameras = pylon.InstantCameraArray(min(len(self.devices)),self.maxCameraToUSe) # create multiple camera
            for i, camera in enumerate(self.cameras):
                camera.Attach(self.tlFactory.CreateDevice(self.devices[i]))
        except genicam.GenericException as e:
            # Error handling
            print("An exception occurred. {}".format(e))
            exitCode = 1
            sys.exit(exitCode)




