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
    print('Default')
    print(ob1.gain, ob1.min_gain, ob1.max_gain)
    print('With custom gain')
    ob1.gain = 10.0
    print(ob1.gain)

    # Test frame rate methods
    print('Default')
    print(ob1.framerate)
    # set method might be removed

    # Test exposure methods
    print('Default')
    print(ob1.exposure, ob1.min_exp, ob1.max_exp)
    print('With custom exposure')
    ob1.exposure = 100.0
    print(ob1.exposure)
    ob1.auto_exp()
    print('Back to AutoExposure')
    print(ob1.exposure)

    ob1.close()
