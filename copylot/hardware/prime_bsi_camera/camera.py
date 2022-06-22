from pyvcam import pvc
from pyvcam.camera import Camera


class PrimeBSICamera:
    def __init__(self):
        pvc.init_pvcam()

    @staticmethod
    def available_cameras():
        cameras = Camera.get_available_camera_names()
        print(f"Available cameras: {cameras}")

        return cameras

    def __del__(self):
        pvc.uninit_pvcam()
