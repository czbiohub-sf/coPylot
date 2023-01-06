from copylot.hardware.orca_camera.dcam import Dcamapi, Dcam

import cv2
import numpy
from copylot.hardware.orca_camera.dcamapi4 import DCAM_IDPROP


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
        self.trigger_source = None
        self.trigger_polarity = None
        self._camera_index = camera_index
        self.dcam = None
        self.exposure_time_ms = None
        self.frame_number = None
        self.trigger_mode = None
        self.devices = None
        self.trigger_times = None
        self.output_trigger_kind = None
        self.output_trigger_polarity = None
        self.master_pulse_mode = None
        self.burst_times = None
        self.master_pulse_trigger = None
        self.buffer_size_frame_number = None

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

    def set_configurations(self, camera_configs, camera_ids=[0]):
        """
        This will set the configuraitons for the hamamatsu camera, but without actually configure it in the hardware.
        this only stores the configuration into the object itself.

        I'm implementing this with similar "pattern" as I used in Daxi-controller for now - Xiyu.

        :return:
        """
        self.exposure_time_ms = camera_configs['exposure time (ms)']
        self.frame_number = camera_configs['frame number']
        self.trigger_mode = camera_configs['trigger mode']
        self.trigger_source = camera_configs['trigger source']
        self.trigger_polarity = camera_configs['trigger polarity']
        self.output_trigger_kind = camera_configs['output trigger kind']
        self.trigger_times = camera_configs['trigger times']
        self.output_trigger_polarity = camera_configs['output trigger polarity']
        self.master_pulse_mode = camera_configs['master pulse mode']
        self.burst_times = camera_configs['burst times']
        self.master_pulse_interval = camera_configs['master pulse interval']
        self.master_pulse_trigger = camera_configs['master pulse trigger']
        self.buffer_size_frame_number = camera_configs['buffer size (frame number)']
        self.xdim = 2048 # todo - implement sub-frame acquisition in the future. camera_configs['xdim']
        self.ydim = 2048 # todo - implement sub-frame acquisition in the future. camera_configs['ydim']

        # make sure all the cameras are open before setting it's configurations.
        for camera_id in camera_ids:
            assert self.devices['camera '+str(camera_id)].is_opened()

        # takeout the Dcam object references.
        if len(camera_ids) != 1:
            print('Only 1 camera is supported right now, now we are using the first detected camera')

        # implement the case with only 1 camera.
        dcam = self.devices['camera '+str(camera_ids[0])]  # take out the dcam object for the camera

        # set exposure time
        v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.EXPOSURETIME,
                                  fValue=self.exposure_time_ms / 1000)  # The unit here seems to be in seconds.
        assert abs(v - self.exposure_time_ms / 1000) < 0.00001  # make sure the exposure time is set correctly.

        # set trigger source
        if self.trigger_source == 'MASTER PULSE':
            v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.TRIGGERSOURCE,
                                      fValue=4)  # fValue = 4 sets the trigger source to be 'MASTER PULSE'
            assert abs(v - 4) < 0.00001  # make sure it is successful.
        else:
            raise ValueError('camera trigger mode was set to ' + str(self.trigger_mode)+'; '
                             'Only \'MASTER PULSE\' is supported'
                            )

        # set trigger mode
        if self.trigger_mode == 'NORMAL':
            v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.TRIGGER_MODE,
                                      fValue=1)  # fValue = 1 sets the trigger mode to be 'NORMAL'.
            assert abs(v - 1) < 0.00001
        else:
            raise ValueError('camera trigger mode set to '+str(self.trigger_mode) + '; '
                             'only \'NORMAL\' is suppoprted.')

        # set trigger polarity
        if self.trigger_polarity == 'POSITIVE':
            v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.TRIGGERPOLARITY,
                                      fValue=2)  # fValue = 2 sets the trigger polarity to be 'POSITIVE', 1 to be negative
            assert abs(v - 2) < 0.00001
        elif self.trigger_polarity == 'NEGATIVE':
            v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.TRIGGERPOLARITY,
                                      fValue=2)  # fValue = 1 sets the trigger polarity to be 'POSITIVE', 1 to be negative
            assert abs(v - 1) < 0.00001
        else:
            raise ValueError('camera trigger polarity is set to '+str(self.trigger_polarity)+'; '
                             'only \'POSITIVE\' and \'NEGATIVE\' are supported.')

        # set trigger times
        v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.TRIGGERTIMES,
                                  fValue=self.trigger_times)  # fValue = 1 sets the trigger times to be 10... find out what it means.
        assert abs(v - self.trigger_times) < 0.00001

        # set output trigger kind
        if self.output_trigger_kind == 'TRIGGER READY':
            v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.OUTPUTTRIGGER_KIND,
                                      fValue=4)  # fValue = 4 sets the output trigger kind to be TRIGGER READY
            assert abs(v - 4) < 0.00001
        else:
            raise ValueError('output trigger kind is set to '+str(self.output_trigger_kind)+'; '
                             'only \'TRIGGER READY\' is supported')

        # set output trigger polairty
        if self.output_trigger_polarity == 'POSITIVE':
            v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.OUTPUTTRIGGER_POLARITY,
                                      fValue=2)  # fValue = 2 sets the trigger polarity to be 'POSITIVE'
            assert abs(v - 2) < 0.00001

        elif self.output_trigger_polarity == 'NEGATIVE':
            v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.OUTPUTTRIGGER_POLARITY,
                                  fValue=1)  # fValue = 2 sets the trigger polarity to be 'POSITIVE'
            assert abs(v - 1) < 0.00001
        else:
            raise ValueError('output trigger polairty is set to '+str(self.output_trigger_polarity)+';'
                             'only \'POSITIVE\' and \'NEGATIVE\' are supported.')

        # set output trigger base sensor
        v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.OUTPUTTRIGGER_BASESENSOR,
                                  fValue=1)  # fValue = 1 sets the output trigger sensor to be 'VIEW 1'.
        assert abs(v - 1) < 0.00001

        # set master pulse mode
        if self.master_pulse_mode == 'CONTINUOUS':
            v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.MASTERPULSE_MODE,
                                      fValue=1)  # fValue = 3 is burst mode, 1 is continuous mode. 2 is start mode.
            assert abs(v - 1) < 0.00001
        elif self.master_pulse_mode == 'START':
            v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.MASTERPULSE_MODE,
                                      fValue=2)  # fValue = 3 is burst mode, 1 is continuous mode. 2 is start mode.
            assert abs(v - 2) < 0.00001
        elif self.master_pulse_mode == 'BURST':
            v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.MASTERPULSE_MODE,
                                      fValue=3)  # fValue = 3 is burst mode, 1 is continuous mode. 2 is start mode.
            assert abs(v - 3) < 0.00001
            # set master pulse burst times

            v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.MASTERPULSE_BURSTTIMES,
                                      fValue=self.burst_times)
            assert abs(v - self.burst_times) < 0.00001
        else:
            raise ValueError('master pulse mode is set to '+str(self.master_pulse_mode)+';'
                             'only \'CONTINUOUS\', \'START\' and \'BURST\' are supported.')

        # set master pulse interval
        v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.MASTERPULSE_INTERVAL,
                                  fValue=self.master_pulse_interval)
        assert abs(v - self.master_pulse_interval) < 0.00001

        # -- set master pulse trigger to be external trigger:
        if self.master_pulse_trigger == 'EXTERNAL':
            v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.MASTERPULSE_TRIGGERSOURCE,
                                      fValue=1)  # this sets the trigger source to be external.
            assert abs(v - 1) < 0.00001
        elif self.master_pulse_trigger == 'SOFTWARE':
            v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.MASTERPULSE_TRIGGERSOURCE,
                                      fValue=2)  # 2 sets the trigger source to be software trigger.
            assert abs(v - 2) < 0.00001
        else:
            raise ValueError('master pulse trigger is set to '+str(self.master_pulse_trigger)+';'
                             'only \'CONTINUOUS\', \'EXTERNAL\' and \'SOFTWARE\' are supported.')

        # allocate buffer
        dcam.buf_alloc(self.buffer_size_frame_number - 1)

    def get_ready(self, camera_ids=[0]):
        """
        This will checkout the camera with the specified camera_id.
        With the Hamamtsu API, this would have to include the following steps:
        1. initiate the dcamapi.

        I'm implementing this with similar "pattern" as I used in Daxi-controller for now - Xiyu.

        :return:
        """
        # 1. initiate the Dcamapi
        Dcamapi.init()

        for camera_id in camera_ids:
            # 2. create the camera device with the camera index
            self.devices = {'camera '+str(camera_id): Dcam(camera_id)}

            # 3. open the camera device
            self.devices['camera '+str(camera_id)].dev_open()

            # 4. make sure the camera is opened
            assert self.devices['camera '+str(camera_id)].is_opened()

    def start(self, camera_ids=[0]):
        """
        This will start the cameres

        I'm implementing this with similar "pattern" as I used in Daxi-controller for now - Xiyu.

        :return:
        """
        for camera_id in camera_ids:
            self.devices['camera '+str(camera_id)].cap_start()

    def capture(self):
        """
        This will capture an image, and return the image as an ndarray

        I'm implementing this with similar "pattern" as I used in Daxi-controller for now - Xiyu.

        :return:
        """
        pass

    def stop(self, camera_ids=[0]):
        """
        this will stop the capturing of the cameras
        I'm implementing this with similar "pattern" as I used in Daxi-controller for now - Xiyu.

        :param camera_ids:
        :return:
        """
        for camera_id in camera_ids:
            self.devices['camera '+str(camera_id)].cap_stop()

    def release_buffer(self, camera_ids=[0]):
        """
        this will release the buffers for all the cameras
        I'm implementing this with similar "pattern" as I used in Daxi-controller for now - Xiyu.

        :param camera_ids:
        :return:
        """
        for camera_id in camera_ids:
            self.devices['camera '+str(camera_id)].buf_release()

    def close(self, camera_ids=[0]):
        """
        This will close the camera device, and un-initi the Dcamapi.

        I'm implementing this with similar "pattern" as I used in Daxi-controller for now - Xiyu.

        :return:
        """
        for camera_id in camera_ids:
            self.devices['camera '+str(camera_id)].dev_close()

        Dcamapi.uninit()
