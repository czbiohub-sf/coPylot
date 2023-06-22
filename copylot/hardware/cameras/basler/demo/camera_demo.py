from copylot.hardware.cameras.basler.camera import BaslerCamera
from pdb import set_trace as st
import tifffile as tf

def camera_snap():
    camera = BaslerCamera()
    camera.activate_camera()
    expo = 10 # set expo to 10 ms
    camera.exposure=expo*1000
    img = camera.snap()
    tf.imshow(img)
    del camera



if __name__ == '__main__':
    # camera_start()

    # camera_set_image_size()

    camera_snap()
