from copylot.hardware.cameras.flir.flir_camera import FlirCamera

if __name__ == '__main__':
    test = FlirCamera()

    # open the system
    test.open()

    # Return 10 frames either taking multiple frames in a single acquisition period or iterating over snap().

    # This is faster, and can control timeout for grabbing images from the camera buffer
    test.snap(n_images=10, wait_time=1000)
    # This is slower, but can introduce delays between beginning/ending camera acquisition
    for i in range(0, 10):
        test.snap()

    # serial number
    print(test.device_id)
    # list of cameras
    print(test.list_available_cameras())

    # open again
    test.open()

    # Test bit depth
    print('Default bit depth', test.bitdepth)
    test.bitdepth = 3
    print('Custom bitdepth', test.bitdepth)

    # Test shutter mode
    print('Default shutter mode', test.shutter_mode)
    test.shutter_mode = 'rolling'
    print('Custom shutter mode', test.shutter_mode)

    # Test binning - THERE ARE SOME SPECIFIC MULTIPLES
    print('Default binsize', test.binning)
    test.binning = (2, 2)
    print('Custom binsize', test.binning)

    # Test image size
    print('Default image size', test.image_size)  # set to the max by default
    print('Limit image size', test.image_size_limits)
    test.image_size = (1000, 2000)
    print('Custom image size', test.image_size)

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
