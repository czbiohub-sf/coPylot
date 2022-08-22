import numpy
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

    def run(self):
        app.run()

    def update(self, data):
        pass
