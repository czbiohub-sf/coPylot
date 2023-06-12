from pypylon import pylon as py
from pypylon import genicam
import sys
exitcode = 0
class BaslerCamera:
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

    def opencam(self):
        try:
            if len(self.devices)<2:
                self.camera = py.InstantCamera(self.tl_factory.GetInstance().CreateFirstDevice())
                self.SensorWmax = self.camera.WidthMax.GetValue()
                self.SensorHmax = self.camera.HeightMax.GetValue()
            else:
                self.camera = py.InstantCameraArray(min(len(self.devices)),
                                                    self.maxCameraToUSe)  # create multiple camera
            # Create and attach all Pylon Devices.
                for idx, cam in enumerate(self.camera):   ### need to add some ways to selectively open cams
                    cam.Attach(self.tl_factory.CreateDevice(self.devices[idx]))
                    # Print the model name of the camera.
                    print("Using device ", cam.GetDeviceInfo().GetModelName())
                    camera_serial = cam.DeviceInfo.GetSerialNumber()
                    print(f"set context {idx} for camera {camera_serial}")
                    cam.SetCameraContext(idx)
                self.SensorWmax = cam.WidthMax.GetValue()
                self.SensorHmax = cam.HeightMax.GetValue()
            self.camera.Open()
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
    def imagesize(self,camnum=None):
        '''

        Returns
        -------
        Size(Height,Width): int
                        retun the currnet image size
        '''


        return self.image_width(camnum),self.image_height(camnum)
    @property
    def image_height(self,camnum=None):
        if camnum is not None:
            height= self.camera[camnum].Height.GetValue()
        else:
            if self.maxCameraToUSe > 1:
                for idx, cam in enumerate(self.camera):
                    height = cam.Height.GetValue()
            else:
                height = self.camera.Height.GetValue()
        print(f"SensorMax Width {} for camera {cam.HeightMax.GetValue()}")

        return height
    @property
    def image_width(self, camnum=None):
        if camnum is not None:
            width = self.camera[camnum].Width.GetValue()
        else:
            if self.maxCameraToUSe > 1:
                for idx, cam in enumerate(self.camera):
                    width = cam.Width.GetValue()
            else:
                width = self.camera.Width.GetValue()
        print(f"SensorMax Width {} for camera {cam.WidthMax.GetValue()}")

        return width
    @property.setter
    def image_height(self,camnum=None,value=None):
        if camnum is not None:
            if value is not None:
                self.camera[camnum].Height.SetValue(value)
            else:
                self.camera[camnum].Height.SetValue(self.SensorHmax)
        else:
            if self.maxCameraToUSe > 1:
                if value is not None:
                    for idx, cam in enumerate(self.camera):
                        cam.Height.SetValue(value)
                els
            else:
                if value is
               self.camera.Height.SetValue()
    @property.setter
    def imagesize(self,camnum=None,value=None):
        if camnum is not None:
            height= self.camera[camnum].Height.SetValue()
            width = self.camera[camnum].Width.GetValue()
        else:
            for idx, cam in enumerate(self.camera):
                height = cam.Height.GetValue()
                width = cam.Width.GetValue()


    def aliviable_acqMode(self):
        '''

        Returns
        -------
        string:
         This will return available Acquisition mode that the camera has
        '''
        return self.cameras[0].AcquisitionMode.GetSymbolics()

    @property
    def acqMode(self,camnum=None):
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

    @acqMode.setter
    def acqMode(self,camnum,value):
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



if __name__ == '__main__':


#     def trigermode(self,cam):
#         cam.Attach(AcquisitionMode.SetValue(AcquisitionMode_SingleFrame);
# )


