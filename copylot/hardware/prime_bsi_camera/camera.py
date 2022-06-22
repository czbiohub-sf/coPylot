from pyvcam import pvc
from pyvcam.camera import Camera


class PrimeBSICamera:
    def __init__(self):
        pass

    @staticmethod
    def available_cameras():
        cameras = Camera.get_available_camera_names()
        print(f"Available cameras: {cameras}")

        return cameras
