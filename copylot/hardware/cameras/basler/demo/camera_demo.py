from copylot.hardware.cameras.basler.camera import BaslerCamera
from pdb import set_trace as st


def camera_start():
    camera = BaslerCamera()
    camera.opencam()

    del camera












if __name__ == '__main__':
    camera_start()

    # camera = BaslerCamera()
    # camera.opencam()
    # st()
    # camera.available_modes()
    # camera.imagesize()
    # camera.closecam()
