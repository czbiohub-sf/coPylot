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
        if Dcamapi.init():
            self.dcam = Dcam(self._camera_index)
            if self.dcam.dev_open():
                self.dcam.buf_alloc(nb_buffer_frames)
                if self.dcam.cap_start():
                    self.timeout_milisec = timeout_milisec
                    self.dcam_status='started'

    def live_capturing_return_images_capture_image(self):
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
        self.dcam.cap_stop()
        self.dcam.buf_release()

