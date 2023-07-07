from copylot.hardware.cameras.abstract_camera import AbstractCamera
from copylot import logger
import PySpin
import numpy as np
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

        # initialize camera
        self.initialize()

    def initialize(self):
        """
        Initialize the current camera. Used for settings or to start imaging.
        """
        try:
            if not self.cam.IsInitialized():
                self.cam.Init()
        except PySpin.SpinnakerException as ex:
            logger.error('Error running camera initialization: %s' % ex)

    def close(self):
        """
        Close the system and delete pointer to current camera after imaging to avoid Spinnaker::Exception [-1004]
        Call open() to image again with this instance
        """
        # Deinitialize camera
        self.cam.DeInit()

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

    def save_image(self, array, n, serial_no):
        """
        Return the nth image data array from an initialized camera.

        Parameters
        ----------
        n: number of images to take in that period of camera initialization. Type: int
        serial_no: serial number of camera. Type: string
        """
        pass
        # get width height info
        # get info of pixel format too?

        # if serial_no:
        #     filename = 'Acquisition-%s-%d.jpg' % (serial_no, n)
        #     while os.path.isfile(
        #             './' + filename
        #     ):  # avoids overwriting if calling snap() multiple times
        #         n = n + 1
        #         filename = 'Acquisition-%s-%d.jpg' % (serial_no, n)
        # else:  # if serial number is empty
        #     filename = 'Acquisition-%d.jpg' % n
        #     while os.path.isfile('./' + filename):
        #         n = n + 1
        #         filename = 'Acquisition-%d.jpg' % (n + 1)
        # #  Save image
        # image_converted.Save(filename)
        # logger.info('Image saved at %s' % filename)

    def return_image(self, processor, processing_type, wait_time):
        """
        Return the nth image data array from an initialized camera.

        Parameters
        ----------
        processor: image processor for post-processing. Type: ImageProcessor
        wait_time: wait time for camera to take one frame in microseconds.
        processing_type:
        """
        #  Retrieve next received image.
        image_result = self.cam.GetNextImage(wait_time)
        if image_result.IsIncomplete():
            logger.warning(
                'Image incomplete with image status %d ...'
                % image_result.GetImageStatus()
            )
            return None
        else:
            width = image_result.GetWidth()
            height = image_result.GetHeight()
            logger.info(f"Image width, height: {width} {height}")

            # Optional color processing. Ex processing_type = PySpin.PixelFormat_Mono8
            if processor is not None:
                image_converted = processor.Convert(image_result, processing_type)
            else:
                image_converted = image_result

            # get 1D numpy array with image data - NOTE that dimensions might vary after processing
            image_array = image_converted.GetNDArray()

            # release image from buffer
            image_result.Release()

            return image_array

    def acquire_images(self, mode, n_images, wait_time, processing, processing_type):
        """
        Acquire a number of images from one camera and save as .jpg files

        Parameters
        ----------
        mode: acquisition mode: 'Continuous' or 'SingleFrame'. Type: string.
        n_images: number of images to be taken >=1. Type: int
        wait_time: timeout to grab images in milliseconds. Type: int
        processing:
        processing_type:
        """
        # Retrieve nodemap
        nodemap = self.cam.GetNodeMap()

        # Cast node entries to CEnumerationPtr
        node_acmod = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
        if not PySpin.IsReadable(node_acmod) or not PySpin.IsWritable(node_acmod):
            logger.error('Unable to set acquisition mode')
            return None

        # Retrieve entry node from enumeration node with each mode
        node_acmod_con = node_acmod.GetEntryByName(mode)

        if not PySpin.IsReadable(node_acmod_con):
            logger.error('Unable to set acquisition mode to ' + mode)
            return None

        # Retrieve integer value from entry node
        acmod_con = node_acmod_con.GetValue()

        # Set integer value from entry node as new value of enumeration node
        node_acmod.SetIntValue(acmod_con)
        logger.info('Acquisition mode set to ' + mode)

        #  Start acquisition
        self.cam.BeginAcquisition()

        processor = None
        # Create ImageProcessor instance for post-processing images
        if processing:
            processor = PySpin.ImageProcessor()
            # Set default image processor color processing method
            processor.SetColorProcessing(
                PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR
            )

        # List to store multiple arrays
        all_arrays = []
        for i in range(n_images):
            try:
                a = self.return_image(processor, processing_type, wait_time)
                all_arrays.append(a[None, :])
            except PySpin.SpinnakerException as ex:
                logger.error('Error on image %i acquisition: %s' % (i, ex))
                return None

        #  End acquisition
        self.cam.EndAcquisition()
        # stack all arrays
        array = np.vstack(all_arrays)

        return array

    def run_single_camera(self, mode, n_images, wait_time, processing, processing_type):
        """
        Run camera for image acquisition

        Parameters
        ----------
        wait_time: timeout to grab the next image in the camera buffer in milliseconds. Type: int
        mode: acquisition mode: 'Continuous' or 'SingleFrame'. Type: string.
        n_images: number of images to be taken >=1. Type: int
        processing:
        processing_type:
        """
        # Call method to acquire images
        try:
            result_array = self.acquire_images(
                mode, n_images, wait_time, processing, processing_type
            )
        except PySpin.SpinnakerException as ex:
            logger.error('Error beginning image acquisition: %s' % ex)
            return None
        return result_array

    def snap(self, n_images=1, wait_time=1000, processing=None, processing_type=None):
        """
        Take and return image arrays of n_images at a time for a single camera.
        Repeatedly calling snap() with begin and end acquisition repeatedly.

        Parameters
        ----------
        wait_time: timeout to grab the next image in the camera buffer in milliseconds. Type: int
        n_images: number of images to be taken >=1. Type: int
        processing:
        processing_type:
        """
        # run
        if n_images == 1:
            mode = 'SingleFrame'
        else:
            mode = 'Continuous'
        return self.run_single_camera(
            mode, n_images, wait_time, processing, processing_type
        )

    @property
    def exposure_limits(self):
        """
        Returns the minimum and maximum exposure in microseconds (type: float)
        """
        return self.cam.ExposureTime.GetMin(), self.cam.ExposureTime.GetMax()

    @property
    def exposure(self):
        """
        Returns the most recent exposure setting in microseconds (type: float)
        """
        return self.cam.ExposureTime.GetValue()

    @exposure.setter
    def exposure(self, exp):
        """
        Set exposure time of one camera (Default is 7280.0 ms). Turns AutoExposure Off

        Parameters
        ----------
        exp: exposure in microseconds. Type: float
        """
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
        return self.cam.Gain.GetMin() / 18.0, self.cam.Gain.GetMax() / 18.0

    @property
    def gain(self):
        """
        Returns the most recent gain setting in dB (type: float)
        """
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

    @property
    def bitdepth(self):
        """
        Return the bit depth of the current camera
        """
        return self.cam.AdcBitDepth.GetValue()

    @bitdepth.setter
    def bitdepth(self, bit):
        """
        Set the bit depth of the current camera to 1, 1.5, or 2. Enter bit = 1,2, or 3, respectively.
        """
        if not PySpin.IsWritable(self.cam.AdcBitDepth()):
            logger.error('Bit depth node is not writable. Try unplugging the camera.')
        self.cam.AdcBitDepth.SetValue(bit)

    def image_nodes(self):
        """
        Get the image size nodes for the current camera
        """
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
        """
        Return the shutter mode of the current camera. 1 = global, 2 = rolling. Type: int
        """
        return self.cam.SensorShutterMode.GetValue()

    @shutter_mode.setter
    def shutter_mode(self, mode='global'):
        """
        Set the shutter mode of the current camera.
        Enter mode = 'global' or 'rolling'
        """
        if mode == 'global':
            if not self.cam.SensorShutterMode.GetValue() == 1:
                self.cam.SensorShutterMode.SetValue(1)
        elif mode == 'rolling':
            if not self.cam.SensorShutterMode.GetValue() == 2:
                self.cam.SensorShutterMode.SetValue(2)
        else:
            logger.error(
                'Mode input: ', mode, ' is not valid. Enter global or rolling mode'
            )
        pass
