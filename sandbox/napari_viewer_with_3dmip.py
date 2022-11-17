import napari
import time

from copylot.hardware.orca_camera.camera import OrcaCamera
from napari._qt.qthreading import thread_worker
from cv2.cv2 import VideoCapture
from napari.layers import Points
from skimage.color import rgb2gray
import numpy as np
from skimage import draw

camera_index = 0


def acquire_image(camera: VideoCapture):
    """
    Acquires an image from a given camera
    """

    # acquire image
    _, picture = camera.read()
    if picture is None:
        return

    # convert to single channel image
    return rgb2gray(picture)


def update_layers(images_data: dict):
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


def get_random_stack():
    stack = np.random.randn(100, 200, 300)
    a1 = int(np.round(np.random.randn(1) * 20)) + 70
    a2 = int(np.round(np.random.randn(1) * 20)) + 170
    a3 = int(np.round(np.random.randn(1) * 20)) + 270

    w1 = int(np.round(np.random.randn(1) * 80)) + 10
    w2 = int(np.round(np.random.randn(1) * 180)) + 10
    w3 = int(np.round(np.random.randn(1) * 280)) + 10

    stack[min(a1, w1):max(a1, w1), min(a2, w2):max(a2, w2), min(a3, w3):max(a3, w3)] = \
        max(stack.ravel()) * 1.5

    # stack = np.transpose(stack, (2,1,0))
    return stack


def get_mips3(stack):
    dim2, dim1, dim0 = stack.shape
    mip01 = np.max(stack, 0)
    mip02 = np.max(stack, 1)
    mip12 = np.max(stack, 2)
    mippatch = np.zeros((dim2, dim2))

    cat0102=np.concatenate((mip01, mip02), axis=0)
    cat1222=np.concatenate((mip12.T,mippatch), axis=0)

    mips3 = np.concatenate((cat0102, cat1222), axis=1)

    return mips3


def process_image(image):
    # estimate maximum position
    from scipy.ndimage import center_of_mass
    y, x = center_of_mass(np.power(image, 10000))

    # put a point around maximum
    points = np.asarray([[y, x]])

    # send dictionary of images back to napari
    return {
        "original": image,
        "brightest point": points
    }


# create a viewer window
viewer = napari.Viewer()

# connect to webcam
camera = VideoCapture(camera_index)


# https://napari.org/guides/stable/threading.html
@thread_worker
def loop_run():
    camera = OrcaCamera()
    camera.live_capturing_return_images_get_ready()

    while True:  # endless loop
        # image = acquire_image(camera)
        image = camera.live_capturing_return_images_capture_image()
        stack = get_random_stack()
        # well what if we have a cube
        mips3 = get_mips3(stack)
        yield {'image': stack,
               'mips3': mips3}
        time.sleep(1)


# Start the loop
worker = loop_run()
worker.yielded.connect(update_layers)
worker.aborted.connect(camera.release)
worker.start()

# Start napari
napari.run()
