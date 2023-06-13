from copylot.hardware.cameras.basler.camera import BaslerCamera

if __name__ == '__main__':
    camera = BaslerCamera()
    camera.opencam()
    camera.acq_mode()
    camera.imagesize()
    camera.aliviable_acqMode()
    camera.closecam()
