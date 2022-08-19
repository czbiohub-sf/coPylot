import numpy
from vispy import scene
from vispy import app
import sys


class Viewer:
    def __init__(self):
        canvas = scene.SceneCanvas(keys='interactive')
        canvas.size = 1024, 1024
        canvas.show()

        # Set up a viewbox to display the image with interactive pan/zoom
        view = canvas.central_widget.add_view()

    def update(self, data: numpy.ArrayLike):
        pass
