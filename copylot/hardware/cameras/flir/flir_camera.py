from copylot.hardware.cameras.abstract_camera import AbstractCamera
from copylot import logger
import PySpin
import os.path


class FlirCameraException(Exception):
    pass


class FlirCamera(AbstractCamera):
    """
    Flir Camera BFS-U3-63S4M-C adapter.
    """

    def __init__(self):
        self.system = None
        self.cam_list = None
        self._cam = None
        self._device_id = None
        self._nodemap_tldevice = None

    @property
    def cam(self):
        """
        Return the CameraPtr of the current camera
        """
        return self._cam

    @cam.setter
    def cam(self, val):
        """
        Set the CameraPtr of the current camera
        """
        self._cam = val

    @property
    def nodemap_tldevice(self):
        """
        Return transport layer device nodemap
        """
        return self._nodemap_tldevice

    @nodemap_tldevice.setter
    def nodemap_tldevice(self, val):
        """
        Set the transport layer device
        """
        self._nodemap_tldevice = val

    @property
    def device_id(self):
        """
        Return the serial number of the current camera (type: String)
        """
        return self._device_id

    @device_id.setter
    def device_id(self, val):
        """
        Set the serial number of the current camera
        """
        self._device_id = val

    def open(self, index=0):
        """
        Open the system before any method can be used. Set a pointer CameraPtr to one camera.

        Parameters
        ----------
        index: index of camera assigned to CameraPtr. Type: int
        """
        if self.system is None:
            self.system = PySpin.System.GetInstance()
            self.cam_list = self.system.GetCameras()
        self.cam = self.cam_list[index]
        self.nodemap_tldevice = self.cam.GetTLDeviceNodeMap()

        # assign serial number
        serial_no = ''
        node_serial_no = PySpin.CStringPtr(
            self.nodemap_tldevice.GetNode('DeviceSerialNumber')
        )
        if PySpin.IsReadable(node_serial_no):
            serial_no = node_serial_no.GetValue()
        else:
            logger.error('Node serial number is not readable')
        self._device_id = serial_no

    def initialize(self):
        """
        Initialize the current camera. Used for settings or to start imaging.
        """
        if not self.cam.IsInitialized():
            self.cam.Init()

    def close(self):
        """
        Close the system and delete pointer to current camera after imaging to avoid Spinnaker::Exception [-1004]
        Call open() to image again with this instance
        """
        # Clean CameraPtr
        self.cam = None
        # Clear camera list
        self.cam_list.Clear()
        # Release system
        self.system.ReleaseInstance()

        # set back to default
        self.system = None
        self.cam_list = None
        self.device_id = None
        self.nodemap_tldevice = None

    def list_available_cameras(self):
        """
        Return the list (type CameraList) of all the cameras in the system
        """
        return self.cam_list

    def save_image(self, n, serial_no, processor, wait_time):
        """
        Save the nth image to take from a given, initialized camera

        Parameters
        ----------
        n: number of images to take in that period of camera initialization. Type: int
        serial_no: serial number of camera. Type: string
        processor: image processor for post-processing. Type: ImageProcessor
        wait_time: wait time for camera to take one frame in microseconds.
        """
        #  Retrieve next received image.
        image_result = self.cam.GetNextImage(wait_time)
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
                while os.path.isfile(
                    './' + filename
                ):  # avoids overwriting if calling snap() multiple times
                    n = n + 1
                    filename = 'Acquisition-%s-%d.jpg' % (serial_no, n)
            else:  # if serial number is empty
                filename = 'Acquisition-%d.jpg' % n
                while os.path.isfile('./' + filename):
                    n = n + 1
                    filename = 'Acquisition-%d.jpg' % (n + 1)
            #  Save image
            image_converted.Save(filename)
            logger.info('Image saved at %s' % filename)
            #  Release image
            image_result.Release()
            return True

    def acquire_images(self, mode='SingleFrame', n_images=1, wait_time=1000):
        """
        Acquire a number of images from one camera and save as .jpg files

        Parameters
        ----------
        mode: acquisition mode: 'Continuous' or 'SingleFrame' by default. Type: string.
        n_images: number of images to be taken >=1. Type: int
        wait_time: timeout to grab images in milliseconds. Type: int
        """
        result = True

        # Retrieve nodemap
        nodemap = self.cam.GetNodeMap()

        # Cast node entries to CEnumerationPtr
        node_acmod = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
        if not PySpin.IsReadable(node_acmod) or not PySpin.IsWritable(node_acmod):
            logger.error('Unable to set acquisition mode')
            return False

        # Retrieve entry node from enumeration node with each mode
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

        # Create ImageProcessor instance for post-processing images
        processor = PySpin.ImageProcessor()
        # Set default image processor color processing method
        processor.SetColorProcessing(
            PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR
        )

        #  Save with device serial number to avoid overwriting filename
        for i in range(n_images):
            try:
                result &= self.save_image(i, self.device_id, processor, wait_time)
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
        mode: acquisition mode: 'Continuous' or 'SingleFrame' by default. Type: string.
        n_images: number of images to be taken >=1. Type: int
        """

        try:
            result = True

            # Initialize camera
            self.initialize()

            # Call method to acquire images
            try:
                result &= self.acquire_images(mode, n_images=n_images)
            except PySpin.SpinnakerException as ex:
                logger.error('Error beginning image acquisition: %s' % ex)
                return False

            # Deinitialize camera
            self.cam.DeInit()  # THIS might set back the settings
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
    def exposure_limits(self):
        """
        Returns the minimum and maximum exposure in microseconds (type: float)
        """
        self.initialize()
        return self.cam.ExposureTime.GetMin(), self.cam.ExposureTime.GetMax()

    @property
    def exposure(self):
        """
        Returns the most recent exposure setting in microseconds (type: float)
        """
        self.initialize()
        return self.cam.ExposureTime.GetValue()

    @exposure.setter
    def exposure(self, exp):
        """
        Set exposure time of one camera (Default is 7280.0 ms). Turns AutoExposure Off

        Parameters
        ----------
        exp: exposure in microseconds. Type: float
        """
        self.initialize()
        if self.cam.ExposureAuto.GetAccessMode() != PySpin.RW:
            logger.error('Unable to disable automatic exposure. Aborting...')

        # Disable automatic exposure
        self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        if self.cam.ExposureTime.GetAccessMode() != PySpin.RW:
            logger.error('Unable to set exposure time')

        # ensure exposure is within bounds
        if self.exposure_limits[0] <= exp <= self.exposure_limits[1]:
            self.cam.ExposureTime.SetValue(exp)
        else:
            logger.error('Input exposure is out of bounds. Cannot change settings')

    def auto_exp(self):
        """
        Return an initialized camera to AutoExposure settings
        """
        # self.cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Continuous)
        pass

    @property
    def gain_limits(self):
        """
        Returns the minimum and maximum gain in dB, normalized to range [0,1] (type: float)
        """
        self.initialize()
        return self.cam.Gain.GetMin() / 18.0, self.cam.Gain.GetMax() / 18.0

    @property
    def gain(self):
        """
        Returns the most recent gain setting in dB (type: float)
        """
        self.initialize()
        return self.cam.Gain.GetValue() / 18.0

    @gain.setter
    def gain(self, g):
        """
        Set gain of one camera (type: float)

        Parameters
        ----------
        g: gain in dB within range [0.0,1.0]. Type: float
        """
        g = g * 18.0
        self.initialize()
        if self.cam.GainAuto.GetAccessMode() != PySpin.RW:
            logger.error('Unable to disable automatic gain')

        # Disable automatic gain
        self.cam.GainAuto.SetValue(PySpin.GainAuto_Off)
        if self.cam.Gain.GetAccessMode() != PySpin.RW:
            logger.error('Unable to set gain')

        # ensure gain is within bounds
        if self.gain_limits[0] <= g <= self.gain_limits[1]:
            self.cam.Gain.SetValue(g)
        else:
            logger.error('Input gain is out of bounds. Cannot change settings')

    @property
    def framerate(self):
        """
        Returns the most recent frame rate setting in Hz (type: float)
        """
        self.initialize()
        return self.cam.AcquisitionFrameRate.GetValue()

    @framerate.setter
    def framerate(self, rate):
        """
        Set frame rate of one camera (default in SpinView 59.65 Hz - the processed FPS differs)

        Parameters
        ----------
        rate: frame rate in Hz. Type: float
        """
        # Disable automatic frame rate
        self.cam.AcquisitionFrameRateAuto = 'Off'
        self.cam.AcquisitionFrameRateAutoEnabled = True
        self.cam.AcquisitionFrame = rate

    def image_nodes(self):
        """
        Get the image size nodes for the current camera
        """
        self.initialize()
        nodemap = self.cam.GetNodeMap()
        node_width = PySpin.CIntegerPtr(nodemap.GetNode('Width'))
        node_height = PySpin.CIntegerPtr(nodemap.GetNode('Height'))
        if not PySpin.IsReadable(node_width) and PySpin.IsWritable(node_width):
            logger.error('Width node is not accessible')
        if not PySpin.IsReadable(node_height) and PySpin.IsWritable(node_height):
            logger.error('Height node is not accessible')
        return node_width, node_height

    @property
    def image_size(self):
        """
        Return the (width, height) of the most recent image size setting in pixels (type: int)
        """
        node_width, node_height = self.image_nodes()
        return node_width.GetValue(), node_height.GetValue()

    @image_size.setter
    def image_size(self, size):
        """
        Set the image size of the current camera

        Parameters
        ----------
        size: tuple for image dimensions in pixels (width, height). Type: int
        """
        node_width, node_height = self.image_nodes()

        # ensure input is within bounds
        minw, maxw, minh, maxh = self.image_size_limits
        if minw <= size[0] <= maxw and minh <= size[1] <= maxh:
            node_width.SetValue(size[0])
            node_height.SetValue(size[1])
        else:
            logger.error('Input image size is out of bounds. Cannot change settings.')

    @property
    def image_size_limits(self):
        """
        Return the image size limits. Type: int
        """
        node_width, node_height = self.image_nodes()
        return (
            node_width.GetMin(),
            node_width.GetMax(),
            node_height.GetMin(),
            node_height.GetMax(),
        )

    @property
    def binning(self):
        self.initialize()
        return (
            self.cam.BinningHorizontal.GetValue(),
            self.cam.BinningVertical.GetValue(),
        )

    @binning.setter
    def binning(self, val):
        """
        Assumes (x,y) binning input
        """
        # CHECK FOR ACCESS ERRORS
        xmin = self.cam.BinningHorizontal.GetMin()
        xmax = self.cam.BinningHorizontal.GetMax()
        ymin = self.cam.BinningVertical.GetMin()
        ymax = self.cam.BinningVertical.GetMax()

        if xmin <= val[0] <= xmax and ymin <= val[1] <= ymax:
            self.cam.BinningHorizontal.SetValue(val[0])
            self.cam.BinningVertical.SetValue(val[1])
        else:
            logger.error('Input binning is out of bounds. Cannot change settings.')

    @property
    def shutter_mode(self):
        pass

    @shutter_mode.setter
    def shutter_mode(self, mode):
        pass

    @property
    def bitdepth(self):
        pass

    @bitdepth.setter
    def bitdepth(self, bit):
        pass
