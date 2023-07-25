from copylot.gui.viewer.viewer import Viewer
from copylot.hardware.cameras.flir.flir_camera import FlirCamera
import numpy as np

# create camera object
cam = FlirCamera()
# open the system
cam.open()


# 2 ways to stream in viewer
# FIRST OPTION: cycle one by one

# function to take and stack an image
def snap_mono(c: FlirCamera):
    snap = c.snap()
    return np.stack((snap, snap, snap), axis=2)


# create initial blank (placeholder) image
init_im = snap_mono(cam)

# create vispy canvas with initial image
view1 = Viewer(init_im)

for i in range(5):
    im = snap_mono(cam)
    view1.update(im)
    view1.process()  # introduces a delay between snapping the images

# run the vispy event loop
view1.run()

# SECOND OPTION: get all images and then cycle them through the viewer
# create vispy canvas with initial image
view2 = Viewer(init_im)

ims = cam.snap(10)
for i in range(10):
    ima = np.stack((ims[i], ims[i], ims[i]), axis=2)
    view2.update(ima)
    view2.process()

view2.run()

cam.close()
