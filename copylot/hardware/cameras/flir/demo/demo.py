from copylot.hardware.cameras.flir.flir_camera import FlirCamera

if __name__ == '__main__':

    ob0 = FlirCamera()

    # Return 1 saved image
    ob0.snap()
    ob0.close()

    # Return 3 saved images
    ob0.multiple(3)
    ob0.close()

    ob1 = FlirCamera()

    # Test gain methods
    assert ob1.gain == 0.0  # default
    assert ob1.min_gain == 0.0
    assert ob1.max_gain == 18.0
    ob1.gain(10.0)  # set gain
    assert ob1.gain == 10.0

    # Test frame rate methods
    assert ob1.framerate == 59.65  # default could be 59.64
    ob1.framerate(40.0)
    assert ob1.framerate == 40.0

    # Test exposure methods
    # 100.0 and 15000.0 are min and max for AUTO-EXPOSURE, but the total limits are further apart
    print('Default')
    print(ob1.exposure, ob1.min_exp, ob1.max_exp)
    print('With custom exposure')
    ob1.exposure = 100.0
    print(ob1.exposure)
    ob1.auto_exp()
    print('Back to AutoExposure')
    print(ob1.exposure)

    ob1.close()
