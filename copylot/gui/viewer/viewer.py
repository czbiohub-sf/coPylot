import numpy as np
from vispy import scene
from vispy import app


class Viewer:
    def __init__(self, img_data=None):
        self.canvas = scene.SceneCanvas(keys='interactive')
        self.canvas.size = 1024, 1024
        self.canvas.title = 'coPylot viewer'
        self.canvas.show()

        # Set up a viewbox to display the image with interactive pan/zoom
        self.view = self.canvas.central_widget.add_view()

        interpolation = 'nearest'

        self.image = scene.visuals.Image(
            img_data,
            interpolation=interpolation,
            parent=self.view.scene,
            method='subdivide',
        )

        # Set 2D camera (the camera will scale to the contents in the scene)
        self.view.camera = scene.PanZoomCamera(aspect=1)
        # flip y-axis to have correct alignment
        self.view.camera.flip = (0, 1, 0)
        self.view.camera.set_range()
        self.view.camera.zoom(1, (250, 200))

        # set parameters for contrast
        self.img_data = img_data
        self._contrast_limits = None
        self.update_freq = 0

    @staticmethod
    def run():
        """
        Start the vispy event loop
        """
        app.run()

    @staticmethod
    def process():
        """
        Update the vispy event loop
        """
        app.process_events()

    def update(self, data):
        """
        Update the data layer of the image in the current viewbox

        Parameters
        ----------
        data: ndarray of the new image to be shown
        """
        # input new image data
        self.image.set_data(data)
        # update the SceneCanvas object
        self.canvas.update()

    @property
    def contrast_limits(self):
        return self._contrast_limits

    @contrast_limits.setter
    def contrast_limits(self, factor):
        # TODO: get tuple as argument, use vispy clim
        pass
