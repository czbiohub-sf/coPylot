from copylot.hardware.cameras.basler.camera import BaslerCamera

if __name__ == '__main__':
    camera = BaslerCamera()
    camera.opencam()
    camera.imagesize()
    camera.acqMode()
    camera.aliviable_acqMode()
    camera.closecam()
