import copy

from copylot.hardware.orca_camera.camera import OrcaCamera


if __name__ == '__main__':
    camera = OrcaCamera()
    camera.live_capturing_return_images_get_ready()
    im1 = camera.live_capturing_return_images_capture_image()
    print('finished capturing')
    k1 = copy.deepcopy(im1)
    im2 = camera.live_capturing_return_images_capture_image()
    k2 = copy.deepcopy(im2)
    im3 = camera.live_capturing_return_images_capture_image()
    print(k1)
    print(k2)
    print(k1-k2)
    type(k1)
    camera.live_capturing_return_images_capture_end()
