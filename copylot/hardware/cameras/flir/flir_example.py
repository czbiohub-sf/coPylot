from flir_camera import FlirCamera

if __name__ == '__main__':
    cam1 = FlirCamera()

    # Return 1 saved image
    cam1.snap()

    # Return 5 saved images
    cam1.multiple(5)
