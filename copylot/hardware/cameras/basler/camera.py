from pypylon import pylon as py
from pypylon import genicam
import sys
exitcode = 0
class BaslerCamera:
    def __init__(self):
        # get transport layer and all attached devices
        self.cameras = None
        self.tl_factory = py.TlFactory.GetInstance()
        self.devices = self.tl_factory.EnumerateDevices()
        if len(self.devices) == 0:
            raise py.RuntimeException("No camera connected")
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
            self.cameras = py.InstantCameraArray(min(len(self.devices)),
                                                    self.maxCameraToUSe)  # create multiple camera
            # Create and attach all Pylon Devices.
            for idx, cam in enumerate(self.cameras):
                cam.Attach(self.tl_factory.CreateDevice(self.devices[idx]))
                # Print the model name of the camera.
                print("Using device ", cam.GetDeviceInfo().GetModelName())
                camera_serial = cam.DeviceInfo.GetSerialNumber()
                print(f"set context {idx} for camera {camera_serial}")
                cam.SetCameraContext(idx)
            self.cameras.Open()

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

        return self.cameras.IsOpen()
    def closecam(self):
        try:
            # Check whether there is any cameras are running and stop the running cam
            if self.cameras.isGrabbing():
                for idx, cam in enumerate(self.cameras):
                    cam.AcquisitionAbort.Execute()
            #close cam
            self.cameras.Close()

        except genicam.GenericException as e:
            # Error handling
            print("An exception occurred. {}".format(e))
            exitcode = 1
            sys.exit(exitcode)

    @property
    def getImagesize(self,camnum):
        '''

        Returns
        -------
        Size(Height,Width): int


        '''
        if camnum is not None:
            height= self.cameras[camnum].Height.GetValue()
            width = self.cameras[camnum].Width.GetValue()
        else:
            for idx, cam in enumerate(self.cameras):
                height = cam.Height.GetValue()
                width = cam.Width.GetValue()
        print(f"SensorMax Width {} for camera {cam.WidthMax.GetValue()}")
        print(f"SensorMax Height {} for camera {cam.HeightMax.GetValue()}")
        return (width,height)

    def aliviableAcqMode(self):
        '''

        Returns
        -------
        string:
         This will return available Acquisition mode that the camera has
        '''
        return self.cameras[0].AcquisitionMode.GetSymbolics()

    @property
    def AcqMode(self,camnum=None):
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
        if camnum is not None:
            value = self.cameras[camnum].AcquisitionMode.GetValue()
        else:
            for idx,cam in enumerate(self.cameras):
                value = cam.AcquisitionMode.GetValue()
        return value

    @AcqMode.setter
    def AcqMode(self,camnum,value):
        '''

        Parameters
        ----------
        camnum:int
            camera number
        value:string
            The AcquisitionMode of the camera, two mode available 'SingleFrame' or 'Continuous'
        '''
        if camnum is not None:
            self.cameras[camnum].AcquisitionMode.SetValue(value)
        else:
            for idx,cam in enumerate(self.cameras):
                cam.AcquisitionMode.SetValue(value)

    def Acqu


if __name__ == '__main__':


#     def trigermode(self,cam):
#         cam.Attach(AcquisitionMode.SetValue(AcquisitionMode_SingleFrame);
# )


