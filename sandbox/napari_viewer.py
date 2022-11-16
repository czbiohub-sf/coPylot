import napari
import time

from napari._qt.qthreading import thread_worker
from cv2.cv2 import VideoCapture
from napari.layers import Points
from skimage.color import rgb2gray
import numpy as np
from skimage import draw

camera_index = 0

def acquire_image(camera : VideoCapture):
    """
    Acquires an image from a given camera
    """

    # acquire image
    _, picture = camera.read()
    if picture is None:
        return

    # convert to single channel image
    return rgb2gray(picture)

def update_layers(images_data : dict):
    """
    Add images to napari is layer or updates a pre-existing layer
    """
    for name in images_data.keys():
        image = images_data[name]
        for layer in viewer.layers:
            if layer.name == name:
                layer.data = image
                image = None
                break

        if image is not None:
            if "point" in name:
                viewer.add_points(image, name=name, face_color='red')
            else:
                viewer.add_image(image, name=name)

def process_image(image):

    # estimate maximum position
    from scipy.ndimage import center_of_mass
    y, x = center_of_mass(np.power(image, 10000))

    # put a point around maximum
    points = np.asarray([[y, x]])

    # send dictionary of images back to napari
    return {
        "original" : image,
        "brightest point" : points
    }

# create a viewer window
viewer = napari.Viewer()

# connect to webcam
camera = VideoCapture(camera_index)

# https://napari.org/guides/stable/threading.html
@thread_worker
def loop_run():
    while True: # endless loop
        # image = acquire_image(camera)
        image = np.random.randn(512,512)
        yield process_image(image)
        time.sleep(0.5)

# Start the loop
worker = loop_run()
worker.yielded.connect(update_layers)
worker.aborted.connect(camera.release)
worker.start()

# Start napari
napari.run()

