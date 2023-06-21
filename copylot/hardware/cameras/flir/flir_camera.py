from copylot.hardware.cameras.abstract_camera import AbstractCamera
from copylot import logger
import PySpin


class FlirCameraException(Exception):
    pass


class FlirCamera(AbstractCamera):
    """
    Flir Camera BFS-U3-63S4M-C adapter.
    """

    # Class to use decorators as exception handlers
    class Decorators(AbstractCamera):
        @classmethod
        def handler(cls, func):
            try:
                return func
            except PySpin.SpinnakerException as ex:
                logger.error(ex)
                return False

    def __init__(self):
        self.system = PySpin.System.GetInstance()
        self.cam_list = self.system.GetCameras()

    @Decorators.handler
    def save_image(self, cam, n, serial_no, processor, wait_time):
        """
        Save the nth image to take from a given, initialized camera

        Parameters
        ----------
        cam: camera to run on. Type: CameraPtr type.
        n: number of images to take in that period of camera initialization. Type: int
        serial_no: serial number of camera. Type: string
        processor: image processor for post-processing. Type: ImageProcessor
        wait_time: wait time for camera to take one frame in microseconds.
        """
        #  Retrieve next received image.
        image_result = cam.GetNextImage(wait_time)
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

    @Decorators.handler
    def acquire_images(
        self,
        cam,
        nodemap,
        nodemap_tldevice,
        mode='SingleFrame',
        n_images=1,
        wait_time=1000,
    ):
        """
        Acquire a number of images from one camera and save as .jpg files

        Parameters
        ----------
        cam: camera to run on. Type: CameraPtr type.
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
        cam.BeginAcquisition()

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
            result &= self.save_image(cam, i, serial_no, processor, wait_time)

        #  End acquisition
        cam.EndAcquisition()

        return result

    @Decorators.handler
    def run_single_camera(self, cam, mode='SingleFrame', n_images=1):
        """ "
        (De)Initialize one camera (after) before acquisition

        Parameters
        ----------
        cam: single input camera. Type: CameraPtr
        mode: acquisition mode: 'Continuous' or 'SingleFrame' by default. Type: string.
        n_images: number of images to be taken >=1. Type: int
        """
        result = True

        # Retrieve TL device nodemap and print device information
        nodemap_tldevice = cam.GetTLDeviceNodeMap()

        # Initialize camera
        cam.Init()

        # Retrieve GenICam nodemap
        nodemap = cam.GetNodeMap()

        # Call method to acquire images
        result &= self.acquire_images(
            cam, nodemap, nodemap_tldevice, mode, n_images=n_images
        )

        # Deinitialize camera
        cam.DeInit()

        return result

    def snap(self):
        """
        Take and save a single frame at a time for 1+ cameras
        """
        result = True
        # num_cameras = self.cam_list.GetSize()
        # print('Number of cameras detected: %d' % num_cameras)

        for i, cam in enumerate(self.cam_list):
            result &= self.run_single_camera(cam)

        # clean up pointer object
        del cam

        # clear camera list
        self.cam_list.Clear()
        # release system instance
        self.system.ReleaseInstance()

        return result

    def multiple(self, n_images):
        """
        Take and save n_images frames for 1+ cameras.

        Parameters
        ----------
        n_images: number of images to be taken >=1. Type: int
        """
        result = True
        for i, cam in enumerate(self.cam_list):
            result &= self.run_single_camera(cam, 'Continuous', n_images)
            del cam

        # clean up pointer object
        # del cam

        # clear camera list
        self.cam_list.Clear()
        # release system instance
        self.system.ReleaseInstance()

        return result

    # Not adding more decorators (at least not yet)
    def get_min_exp(self, cam):
        """
        Returns the minimum exposure of one camera (cam, type CameraPtr) in microseconds
        """
        return cam.ExposureTime.GetMin()

    def get_max_exp(self, cam):
        """
        Returns the maximum exposure of one camera (cam, type CameraPtr) in microseconds
        """
        return cam.ExposureTime.GetMax()

    def get_exposure(self, cam):
        """
        Returns the most recent exposure setting of one camera (cam, type CameraPtr) in microseconds
        """
        return cam.ExposureTime.GetValue()

    def set_exposure(self, cam, exp):
        """
        Set exposure time of one camera (Default is 5 ms)

        Parameters
        ----------
        cam: single input camera. Type: CameraPtr
        exp: exposure in microseconds. Type: int
        """
        result = True

        if cam.ExposureAuto.GetAccessMode() != PySpin.RW:
            logger.error('Unable to disable automatic exposure. Aborting...')
            return False

        # Disable automatic exposure
        cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        if cam.ExposureTime.GetAccessMode() != PySpin.RW:
            logger.error('Unable to set exposure time')
            return False

        # Ensure desired exposure time does not exceed the max or min
        exp = min(self.get_max_exp(cam), exp)
        exp = max(self.get_min_exp(cam), exp)
        cam.ExposureTime.SetValue(exp)

        return result

    def get_min_gain(self, cam):
        """
        Returns the minimum gain of one camera (cam, type CameraPtr) in dB
        """
        return cam.Gain.GetMin()

    def get_max_gain(self, cam):
        """
        Returns the maximum gain of one camera (cam, type CameraPtr) in dB
        """
        return cam.Gain.GetMax()

    def get_gain(self, cam):
        """
        Returns the most recent gain setting of one camera (cam, type CameraPtr) in dB
        """
        return cam.Gain.GetValue()

    def set_gain(self, cam, gain):
        """
        Set gain of one camera.

        Parameters
        ----------
        cam: single input camera. Type: CameraPtr
        gain: gain in dB. Type: int
        """
        result = True

        if cam.GainAuto.GetAccessMode() != PySpin.RW:
            logger.error('Unable to disable automatic gain')
            return False

        # Disable automatic gain
        cam.GainAuto.SetValue(PySpin.GainAuto_Off)
        if cam.Gain.GetAccessMode() != PySpin.RW:
            logger.error('Unable to set gain')
            return False

        # ensure gain is higher than min and lower than max
        gain = min(self.get_max_gain(cam), gain)
        gain = max(self.get_min_gain(cam), gain)
        cam.Gain.SetValue(gain)

        return result
