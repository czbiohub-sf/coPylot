class Camera:
    def __init__(self, camera_index: int = 0):
        self._camera_index = camera_index

    def run(self):
        raise NotImplementedError
