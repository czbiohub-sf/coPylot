from copylot.hardware.hamamatsu_camera.dcam import Dcamapi, Dcam
from napari._qt.qthreading import thread_worker


class Camera:
    def __init__(self, camera_index: int = 0):
        self._camera_index = camera_index

    def run(self, visualization_napari_layer):
        worker = self.threaded_run(visualization_napari_layer)
        worker.start()

    @thread_worker
    def threaded_run(self, visualization_napari_layer, nb_frame: int = 100000):
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
                                data = dcam.buf_getlastframedata()  # Data is here
                                visualization_napari_layer.data = data
                                print("data is here")
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
                        print(f"dcam.cap_start() fails with error {dcam.lasterr()}")

                    dcam.buf_release()  # release buffer
                else:
                    print(
                        f"dcam.buf_alloc({nb_buffer_frames}) fails with error {dcam.lasterr()}"
                    )
                dcam.dev_close()
            else:
                print(f"dcam.dev_open() fails with error {dcam.lasterr()}")
        else:
            print(f"Dcamapi.init() fails with error {Dcamapi.lasterr()}")

        Dcamapi.uninit()
