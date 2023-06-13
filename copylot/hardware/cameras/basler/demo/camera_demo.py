from copylot.hardware.cameras.basler.camera import BaslerCamera
from pdb import set_trace as st


def camera_start():
    camera = BaslerCamera()
    camera.opencam()

    del camera


def camera_para():
    camera = BaslerCamera()
    camera.opencam()
    camera.available_modes()
    print(camera.imagesize())
    del camera


def camera_set_image_size():
    camera = BaslerCamera()
    camera.opencam()
    camera.available_modes()
    print(camera.imagesize())
    width = 2048
    height = 2048
    camera.image_width = width
    camera.image_height = height
    print(camera.imagesize())

    del camera




if __name__ == '__main__':
    # camera_start()

    # camera_set_image_size()

