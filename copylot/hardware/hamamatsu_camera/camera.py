from copylot.hardware.hamamatsu_camera.dcam import Dcamapi, Dcam


class CameraException(Exception):
    pass


class Camera:
    def __init__(self, camera_index: int = 0):
        self._camera_index = camera_index

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
                                data = (
                                    dcam.buf_getlastframedata()
                                )  # Data is here  # noqa: F841
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
                        raise CameraException(
                            f"dcam.cap_start() fails with error {dcam.lasterr()}"
                        )

                    dcam.buf_release()  # release buffer
                else:
                    raise CameraException(
                        f"dcam.buf_alloc({nb_buffer_frames}) fails with error {dcam.lasterr()}"
                    )
                dcam.dev_close()
            else:
                raise CameraException(
                    f"dcam.dev_open() fails with error {dcam.lasterr()}"
                )
        else:
            raise CameraException(
                f"Dcamapi.init() fails with error {Dcamapi.lasterr()}"
            )

        Dcamapi.uninit()
