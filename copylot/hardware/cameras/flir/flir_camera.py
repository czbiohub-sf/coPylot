from copylot.hardware.cameras.abstract_camera import AbstractCamera
from copylot import logger
import PySpin


class FlirCameraException(Exception):
    pass


class FlirCamera(AbstractCamera):
    """
    Flir Camera BFS-U3-63S4M-C adapter.
    """

    def __init__(self, index=0):
        self._system = PySpin.System.GetInstance()
        self.cam_list = self.system.GetCameras()
        self._cam = self.cam_list[index]

    @property
    def system(self):
        return self._system

    @property
    def cam(self):
        return self._cam

    @cam.setter
    def cam(self, index):
        self._cam = self.cam_list[index]

    @cam.deleter
    def cam(self):
        del self._cam

    def setting(self):
        """
        Initializes camera to access settings
        """
        if not self.cam.IsInitialized():
            self.cam.Init()

    def close(self):
        """
        Irreversibly close the system after imaging to avoid Spinnaker::Exception [-1004]

        User should call close() *after* calling snap(), multiple() as many times as needed for the same
        instance with custom settings. Further imaging requires creating a new instance.
        """
        # clean up camera pointer
        del self.cam
        # Clear camera list
        self.cam_list.Clear()
        # Release system
        self.system.ReleaseInstance()

    def save_image(self, n, serial_no, processor, wait_time):
        """
        Save the nth image to take from a given, initialized camera

        Parameters
        ----------
        self.cam:
        n: number of images to take in that period of camera initialization. Type: int
        serial_no: serial number of camera. Type: string
        processor: image processor for post-processing. Type: ImageProcessor
        wait_time: wait time for camera to take one frame in microseconds.
        """
        #  Retrieve next received image.
        image_result = self.cam.GetNextImage(wait_time)
        #  Ensure image completion
        if image_result.IsIncomplete():
            logger.warning(
                'Image incomplete with image status %d ...'
                % image_result.GetImageStatus()
            )
            return False
        else:
            #  some image information
            width = image_result.GetWidth()
            height = image_result.GetHeight()
            logger.info(f"Image width, height: {width} {height}")

            #  Convert image to mono 8. Converted has no need to be released. Optional color processing.
            image_converted = processor.Convert(image_result, PySpin.PixelFormat_Mono8)
            # Create a unique filename
            if serial_no:
                filename = 'Acquisition-%s-%d.jpg' % (serial_no, n)
            else:  # if serial number is empty
                filename = 'Acquisition-%d.jpg' % n
            #  Save image
            image_converted.Save(filename)
            logger.info('Image saved at %s' % filename)
            #  Release image
            image_result.Release()
            return True

    def acquire_images(
        self, nodemap, nodemap_tldevice, mode='SingleFrame', n_images=1, wait_time=1000
    ):
        """
        Acquire a number of images from one camera and save as .jpg files

        Parameters
        ----------
        self.cam:
        nodemap: device nodemap. Type: INodeMap type.
        nodemap_tldevice: transport layer device nodemap. Type: INodeMap.
        mode: acquisition mode: 'Continuous' or 'SingleFrame' by default. Type: string.
        n_images: number of images to be taken >=1. Type: int
        wait_time: timeout to grab images in milliseconds. Type: int
        """
        result = True

        # Cast node entries to CEnumerationPtr
        node_acmod = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
        if not PySpin.IsReadable(node_acmod) or not PySpin.IsWritable(node_acmod):
            logger.error('Unable to set acquisition mode')
            return False

        # Retrieve entry node from enumeration node with each mode
        if n_images != 1:
            node_acmod_con = node_acmod.GetEntryByName(mode)
        else:
            node_acmod_con = node_acmod.GetEntryByName(mode)

        if not PySpin.IsReadable(node_acmod_con):
            logger.error('Unable to set acquisition mode to ' + mode)
            return False

        # Retrieve integer value from entry node
        acmod_con = node_acmod_con.GetValue()

        # Set integer value from entry node as new value of enumeration node
        node_acmod.SetIntValue(acmod_con)
        logger.info('Acquisition mode set to ' + mode)

        #  Start acquisition
        self.cam.BeginAcquisition()

        #  Retrieve device serial number to avoid overwriting filename
        serial_no = ''
        node_serial_no = PySpin.CStringPtr(
            nodemap_tldevice.GetNode('DeviceSerialNumber')
        )
        if PySpin.IsReadable(node_serial_no):
            serial_no = node_serial_no.GetValue()
            logger.info('Device serial number retrieved as %s...' % serial_no)

        # Create ImageProcessor instance for post-processing images
        processor = PySpin.ImageProcessor()
        # Set default image processor color processing method
        processor.SetColorProcessing(
            PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR
        )

        for i in range(n_images):
            try:
                result &= self.save_image(i, serial_no, processor, wait_time)
            except PySpin.SpinnakerException as ex:
                logger.error('Error on image %i acquisition: %s' % (i, ex))
                return False

        #  End acquisition
        self.cam.EndAcquisition()

        return result

    def run_single_camera(self, mode='SingleFrame', n_images=1):
        """ "
        (De)Initialize one camera (after) before acquisition

        Parameters
        ----------
        self.cam:
        mode: acquisition mode: 'Continuous' or 'SingleFrame' by default. Type: string.
        n_images: number of images to be taken >=1. Type: int
        """

        try:
            result = True

            # Retrieve TL device nodemap and print device information
            nodemap_tldevice = self.cam.GetTLDeviceNodeMap()

            # Initialize camera
            self.cam.Init()

            # Retrieve GenICam nodemap
            nodemap = self.cam.GetNodeMap()

            # Call method to acquire images
            try:
                result &= self.acquire_images(
                    nodemap, nodemap_tldevice, mode, n_images=n_images
                )
            except PySpin.SpinnakerException as ex:
                logger.error('Error beginning image acquisition: %s' % ex)
                return False

            # Deinitialize camera
            self.cam.DeInit()
            return result

        except PySpin.SpinnakerException as ex:
            logger.error('Error running camera initialization: %s' % ex)
            return False

    def snap(self):
        """
        Take and save a single frame at a time for a single camera.
        """
        result = True

        # run
        result &= self.run_single_camera()
        return result

    def multiple(self, n_images):
        """
        Take and save n_images frames for a single camera

        Parameters
        ----------
        n_images: number of images to be taken >=1. Type: int
        """
        result = True

        # run and close system
        result &= self.run_single_camera('Continuous', n_images)
        return result

    @property
    def min_exp(self):
        """
        Returns the minimum exposure in microseconds
        """
        self.setting()
        return self.cam.ExposureTime.GetMin()

    @property
    def max_exp(self):
        """
        Returns the maximum exposure in microseconds
        """
        self.setting()
        return self.cam.ExposureTime.GetMax()

    @property
    def exposure(self):
        """
        Returns the most recent exposure setting in microseconds
        """
        self.setting()
        return self.cam.ExposureTime.GetValue()

    @exposure.setter
    def exposure(self, exp):
        """
        Set exposure time of one camera (Default is 7280.0 ms). Turns AutoExposure Off

        Parameters
        ----------
        exp: exposure in microseconds. Type: int
        """
        self.setting()
        if self.cam.ExposureAuto.GetAccessMode() != PySpin.RW:
            logger.error('Unable to disable automatic exposure. Aborting...')

        # Disable automatic exposure
        self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        if self.cam.ExposureTime.GetAccessMode() != PySpin.RW:
            logger.error('Unable to set exposure time')

        # Ensure desired exposure time does not exceed the max or min
        exp = min(self.max_exp, exp)
        exp = max(self.min_exp, exp)
        self.cam.ExposureTime.SetValue(exp)

    def auto_exp(self):
        """
        Return an initialized camera to AutoExposure settings
        TODO revise this
        """
        # self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Continuous)
        # self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Once)
        pass

    @property
    def min_gain(self):
        """
        Returns the minimum gain in dB
        """
        return self.cam.Gain.GetMin()

    @property
    def max_gain(self):
        """
        Returns the maximum gain in dB
        """
        return self.cam.Gain.GetMax()

    @property
    def gain(self):
        """
        Returns the most recent gain setting in dB
        """
        return self.cam.Gain.GetValue()

    @gain.setter
    def gain(self, g):
        """
        Set gain of one camera (default is 0.0)

        Parameters
        ----------
        g: gain in dB. Type: int
        """
        if self.cam.GainAuto.GetAccessMode() != PySpin.RW:
            logger.error('Unable to disable automatic gain')

        # Disable automatic gain
        self.cam.GainAuto.SetValue(PySpin.GainAuto_Off)
        if self.cam.Gain.GetAccessMode() != PySpin.RW:
            logger.error('Unable to set gain')

        # ensure gain is higher than min and lower than max
        gain = min(self.max_gain, g)
        gain = max(self.min_gain, g)
        self.cam.Gain.SetValue(g)

    @property
    def framerate(self):
        """
        Returns the most recent frame rate setting in Hz
        """
        return self.cam.AcquisitionFrameRate.GetValue()

    @framerate.setter
    def framerate(self, rate):
        """
        Set frame rate of one camera (default in SpinView 59.65 Hz - the processed FPS differs)

        Parameters
        ----------
        rate: frame rate in Hz. Type: int
        """
        # Disable automatic frame rate
        self.cam.AcquisitionFrameRateAuto = 'Off'
        self.cam.AcquisitionFrameRateAutoEnabled = True
        self.cam.AcquisitionFrame = rate
