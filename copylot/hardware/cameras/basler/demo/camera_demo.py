from copylot.hardware.cameras.basler.camera import BaslerCamera
from copylot.hardware.cameras.basler.camera import GrabStrategy
from pdb import set_trace as st
import tifffile as tf
import time


##### example of start the camera #####
def camera_start_test():
    camera = BaslerCamera()
    camera.activate_camera()
    expo = 10 # set expo to 10 ms
    camera.exposure=expo*1000
    # camera.trigger = 'Off'
    camera.config_trigger()
        # img = camera.snap()
    # tf.imshow(img)
    del camera

##### example of snap one image #####
def camera_snap():
    camera = BaslerCamera()
    camera.activate_camera()
    expo = 10 # set expo to 10 ms
    camera.exposure=expo*1000
    camera.config_trigger()
    camera.start_acquisition(GrabStrategy.ONE_BY_ONE)
    img = camera.snap()
    del camera







if __name__ == '__main__':
    camera_snap()

    # camera_set_image_size()

    # camera_test()


