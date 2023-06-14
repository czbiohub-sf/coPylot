from copylot.hardware.cameras.basler.camera import BaslerCamera
from pdb import set_trace as st


def camera_start():
    camera = BaslerCamera()
    camera.opencam()

    del camera


def camera_para():
    camera = BaslerCamera()
    camera.opencam()
    print(camera.imagesize())
    del camera


def camera_set_image_size():
    camera = BaslerCamera()
    camera.opencam()
    print(camera.imagesize())
    width = 3000
    height = 3000
    camera.image_width = width
    camera.image_height = height
    print(camera.imagesize())

    del camera


def camera_set_trigger_type():
    camera = BaslerCamera()
    camera.opencam()
    print(camera.imagesize())
    print(camera.pixel_format)
    camera.pixel_format_options
    camera.image_width=4000
    camera.image_height=4000
    camera.trigger_type_options
    camera.pixel_format = 'Mono10'
    camera.pixel_format
    del camera


if __name__ == '__main__':
    # camera_start()

    # camera_set_image_size()

    camera_set_image_size()
