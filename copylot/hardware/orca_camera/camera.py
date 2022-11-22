from copylot.hardware.orca_camera.dcam import Dcamapi, Dcam

import cv2
import numpy


def dcamtest_show_framedata(data, windowtitle, iShown):
    """
    Show numpy buffer as an image

    Arg1:   NumPy array
    Arg2:   Window name
    Arg3:   Last window status.
        0   open as a new window
        <0  already closed
        >0  already openend
    """
    if iShown > 0 and cv2.getWindowProperty(windowtitle, 0) < 0:
        return -1  # Window has been closed.

    if iShown < 0:
        return -1  # Window is already closed.

    if data.dtype == numpy.uint16:
        imax = numpy.amax(data)
        if imax > 0:
            imul = int(65535 / imax)
            # print('Multiple %s' % imul)
            data = data * imul

        cv2.imshow(windowtitle, data)
        return 1
    else:
        print('-NG: dcamtest_show_image(data) only support Numpy.uint16 data')
        return -1


class OrcaCameraException(Exception):
    pass


class OrcaCamera:
    """
    Hamamatsu Orca Flash 4 Camera adapter.

    Parameters
    ----------
    camera_index : int

    """

    def __init__(self, camera_index: int = 0):

        self._camera_index = camera_index
        self.dcam = None
        self.exposure_time_ms = None
        self.frame_number = None
        self.trigger_mode = None
        self.output_trigger = None
        self.devices = None

    def run(self, nb_frame: int = 100000):
        """
        Method to run the camera. It handles camera initializations and
        uninitializations as well as camera buffer allocation/deallocation.

        Parameters
        ----------
        nb_frame : int
            Number of frames to be acquired, default chosen just a big enough number.

        """
        if Dcamapi.init():
            dcam = Dcam(self._camera_index)
            if dcam.dev_open():
                nb_buffer_frames = 3
                if dcam.buf_alloc(nb_buffer_frames):

                    if dcam.cap_start():
                        timeout_milisec = 20

                        for _ in range(nb_frame):
                            if dcam.wait_capevent_frameready(timeout_milisec):
                                data = (  # noqa: F841
                                    dcam.buf_getlastframedata()
                                )  # Data is here
                                print(data.shape, type(data))
                            else:
                                dcamerr = dcam.lasterr()
                                if dcamerr.is_timeout():
                                    print("===: timeout")
                                else:
                                    print(
                                        f"dcam.wait_event() fails with error {dcamerr}"
                                    )
                                    break

                        dcam.cap_stop()
                    else:
                        raise OrcaCameraException(
                            f"dcam.cap_start() fails with error {dcam.lasterr()}"
                        )

                    dcam.buf_release()  # release buffer
                else:
                    raise OrcaCameraException(
                        f"dcam.buf_alloc({nb_buffer_frames}) fails with error {dcam.lasterr()}"
                    )
                dcam.dev_close()
            else:
                raise OrcaCameraException(
                    f"dcam.dev_open() fails with error {dcam.lasterr()}"
                )
        else:
            raise OrcaCameraException(
                f"Dcamapi.init() fails with error {Dcamapi.lasterr()}"
            )

        Dcamapi.uninit()

    def live_capturing_and_show(self):
        """
        this function uses the orca camera for live capturing function, and display it in a cv2 window.

        I'm now implementing some methods in a way that doesn't change anything in __init__() and run() that was already
        there when I started.
        Will re-organize these after discussion with AhmetCan.
        -- Xiyu, 2022-11-16

        highly possible we will delete this method after the discussion.
        :return:
        """
        if Dcamapi.init():
            dcam = Dcam(self._camera_index)
            if dcam.dev_open():
                nb_buffer_frames = 3
                if dcam.buf_alloc(nb_buffer_frames):
                    # dcamtest_thread_live(dcam)
                    if dcam.cap_start():
                        timeout_milisec = 100
                        iwindowstatus = 0
                        while iwindowstatus >= 0:
                            if dcam.wait_capevent_frameready(timeout_milisec) is not False:
                                data = dcam.buf_getlastframedata()
                                iwindowstatus = dcamtest_show_framedata(data, 'test', iwindowstatus)
                            else:
                                dcamerr = dcam.lasterr()
                                if dcamerr.is_timeout():
                                    print('===: timeout')
                                else:
                                    print('-NG: Dcam.wait_event() fails with error {}'.format(dcamerr))
                                    break

                            key = cv2.waitKey(1)
                            if key == ord('q') or key == ord('Q'):  # if 'q' was pressed with the live window, close it
                                break

                        dcam.cap_stop()

                    dcam.buf_release()  # release buffer
                else:
                    print('-NG: Dcam.buf_alloc(3) fails with error {}'.format(dcam.lasterr()))
                dcam.dev_close()

        Dcamapi.uninit()

    def live_capturing_return_images_get_ready(self, nb_buffer_frames=3, timeout_milisec=100):
        """
        this function only initialize the Dcamapi, allocate buffer, let capturing start for live capturing of images
        using the orca camera. I'm calling it get_ready.

        I'm now implementing some methods in a way that doesn't change anything in __init__() and run() that was already
        there when I started.
        Will re-organize these after discussion with AhmetCan.
        -- Xiyu, 2022-11-16
        :return:
        """

        if Dcamapi.init():
            self.dcam = Dcam(self._camera_index)
            if self.dcam.dev_open():
                self.dcam.buf_alloc(nb_buffer_frames)
                if self.dcam.cap_start():
                    self.timeout_milisec = timeout_milisec
                    self.dcam_status='started'

    def live_capturing_return_images_capture_image(self):
        """
        this function captures an image and return the captured image as an ndarray.

        I'm now implementing some methods in a way that doesn't change anything in __init__() and run() that was already
        there when I started.
        Will re-organize these after discussion with AhmetCan.
        -- Xiyu, 2022-11-16

        highly possible we will delete this method after the discussion.
        :return:
        """

        if self.dcam_status=='started':
            if self.dcam.wait_capevent_frameready(self.timeout_milisec) is not False:
                print('capture the image')
                self.data = self.dcam.buf_getlastframedata()
            else:
                dcamerr = self.dcam.lasterr()
                if dcamerr.is_timeout():
                    print('===: timeout')
                else:
                    print('Dcam.wait_event() fails with error{}'.format(dcamerr))
        return self.data

    def live_capturing_return_images_capture_end(self):
        """
        this function closes up the camera, and the buffer, and uninit the api.

        I'm now implementing some methods in a way that doesn't change anything in __init__() and run() that was already
        there when I started.
        Will re-organize these after discussion with AhmetCan.
        -- Xiyu, 2022-11-16

        highly possible we will delete this method after the discussion.
       :return:
        """

        self.dcam.cap_stop()
        self.dcam.buf_release()
        Dcamapi.uninit()

    def set_configurations(self, camera_configs):
        """
        This will set the configuraitons for the hamamatsu camera, but without actually configure it in the hardware.
        this only stores the configuration into the object itself.

        I'm implementing this with similar "pattern" as I used in Daxi-controller for now - Xiyu.

        :return:
        """
        self.exposure_time_ms = camera_configs['exposure time (ms)']
        self.frame_number = camera_configs['frame number']
        self.trigger_mode = camera_configs['trigger mode']
        self.output_trigger = camera_configs['output trigger']

    def get_ready(self, camera_id=0):
        """
        This will checkout the camera with the specified camera_id.
        With the Hamamtsu API, this would have to include the following steps:
        1. initiate the dcamapi.

        I'm implementing this with similar "pattern" as I used in Daxi-controller for now - Xiyu.

        :return:
        """
        # 1. initiate the Dcamapi
        Dcamapi.init()

        # 2. create the camera device with the camera index
        self.devices = {'camera '+str(camera_id): Dcam(camera_id)}

        # 3. open the camera device
        self.devices['camera '+str(camera_id)].dev_open()

        # set the configurations for the camera
        # self.devices['camera ' + str(camera_id)].prop_setgetvalue()




    def start(self):
        """
        This will

        I'm implementing this with similar "pattern" as I used in Daxi-controller for now - Xiyu.

        :return:
        """
        pass

    def capture(self):
        """
        This will capture an image, and return the image as an ndarray

        I'm implementing this with similar "pattern" as I used in Daxi-controller for now - Xiyu.

        :return:
        """
        pass

    def close(self):
        """
        This will close the camera device, and un-initi the Dcamapi.

        I'm implementing this with similar "pattern" as I used in Daxi-controller for now - Xiyu.

        :return:
        """
        pass

