from copylot.hardware.cameras.flir.flir_camera import FlirCamera

if __name__ == '__main__':
    test = FlirCamera()

    # open the system
    test.open()

    # serial number
    print(test.device_id)
    # list of cameras
    print(test.list_available_cameras())

    # Return 10 frames and save output arrays as .csv files (this can be changed)

    # Option 1: take multiple frames in a single acquisition
    # Can control timeout (wait_time) for grabbing images from the camera buffer
    snap1 = test.snap(n_images=5, wait_time=1000)
    test.save_image(snap1)
    # Option 2: iterate over snap()
    # Saving in each iteration causes a delay between beginning/ending camera acquisition
    # Could also collect the snap2 outputs and then save outside the loop to avoid delays
    # (which is just what Option 1 does implicitly)
    for i in range(0, 5):
        snap2 = test.snap()
        test.save_image(snap2)

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
