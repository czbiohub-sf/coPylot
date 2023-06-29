from copylot.hardware.cameras.flir.flir_camera import FlirCamera

if __name__ == '__main__':
    test = FlirCamera()

    # open the system
    test.open()

    # serial number
    print(test.device_id)
    # list of cameras
    print(test.list_available_cameras())

    # Return saved images
    test.snap()
    test.snap()

    # close system
    test.close()

    # open again
    test.open()

    # Test gain methods
    print('Default AutoGain', test.gain, test.gain_limits)
    test.gain = 0.8
    print('Custom gain', test.gain)

    # Test exposure methods
    print('Default AutoExposure', test.exposure, test.exposure_limits)
    test.exposure = 100.0
    print('Custom exposure', test.exposure)

    # Test frame rate methods
    print('Default frame rate', test.framerate)
    # set method might be removed

    test.close()
