from copylot.hardware.cameras.abstract_camera import AbstractCamera
from copylot import logger
import PySpin


class FlirCameraException(Exception):
    pass


class FlirCamera(AbstractCamera):
    """
    Flir Camera BFS-U3-63S4M-C adapter.
    """

    def __init__(self):
        self.system = PySpin.System.GetInstance()
        self.cam_list = self.system.GetCameras()

    def acquire_images(
        self, cam, nodemap, nodemap_tldevice, mode='SingleFrame', n_images=1
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
        """

        try:
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
                node_acmod_con = node_acmod.GetEntryByName(mode)  # SPELLING
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

            logger.info('Acquisition started')

            #  Retrieve device serial number to avoid overwriting filename
            device_serial_number = ''
            node_device_serial_number = PySpin.CStringPtr(
                nodemap_tldevice.GetNode('DeviceSerialNumber')
            )
            if PySpin.IsReadable(node_device_serial_number):
                device_serial_number = node_device_serial_number.GetValue()
                logger.info(
                    'Device serial number retrieved as %s...' % device_serial_number
                )

            # Create ImageProcessor instance for post-processing images
            processor = PySpin.ImageProcessor()

            # Set default image processor color processing method
            processor.SetColorProcessing(
                PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR
            )

            for i in range(n_images):
                try:

                    #  Retrieve next received image. 1s wait time. Raw images have to be released from the buffer
                    image_result = cam.GetNextImage(1000)

                    #  Ensure image completion
                    if image_result.IsIncomplete():
                        logger.warning(
                            'Image incomplete with image status %d ...'
                            % image_result.GetImageStatus()
                        )

                    else:

                        #  some image information
                        width = image_result.GetWidth()
                        height = image_result.GetHeight()
                        logger.info(
                            'Grabbed Image %d, width = %d, height = %d'
                            % (i, width, height)
                        )

                        #  Convert image to mono 8. Converted has no need to be released. Optional color processing.
                        image_converted = processor.Convert(
                            image_result, PySpin.PixelFormat_Mono8
                        )

                        # Create a unique filename
                        if device_serial_number:
                            filename = 'Acquisition-%s-%d.jpg' % (
                                device_serial_number,
                                i,
                            )
                        else:  # if serial number is empty
                            filename = 'Acquisition-%d.jpg' % i

                        #  Save image
                        image_converted.Save(filename)
                        logger.info('Image saved at %s' % filename)

                        #  Release image
                        image_result.Release()

                except PySpin.SpinnakerException as ex:
                    logger.error('Error: %s' % ex)
                    return False

            #  End acquisition
            cam.EndAcquisition()

        except PySpin.SpinnakerException as ex:
            logger.error('Error: %s' % ex)
            return False

        return result

    def run_single_camera(self, cam, mode='SingleFrame', n_images=1):
        """ "
        (De)Initialize one camera (after) before acquisition

        Parameters
        ----------
        cam: single input camera. Type: CameraPtr
        mode: acquisition mode: 'Continuous' or 'SingleFrame' by default. Type: string.
        n_images: number of images to be taken >=1. Type: int
        """

        try:
            result = True

            # Retrieve TL device nodemap and print device information
            nodemap_tldevice = cam.GetTLDeviceNodeMap()

            # Initialize camera
            cam.Init()

            # Retrieve GenICam nodemap
            nodemap = cam.GetNodeMap()

            # Call method to acquire images
            self.acquire_images(cam, nodemap, nodemap_tldevice, mode, n_images=n_images)

            # Deinitialize camera
            cam.DeInit()

        except PySpin.SpinnakerException as ex:
            logger.error('Error: %s' % ex)
            result = False

        return result

    def snap(self):
        """
        Take and save a single frame at a time for 1+ cameras
        """
        result = True
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

        # clean up pointer object
        del cam
        # clear camera list
        self.cam_list.Clear()
        # release system instance
        self.system.ReleaseInstance()

        return result
