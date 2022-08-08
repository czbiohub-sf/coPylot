from time import sleep

from copylot.hardware.laser.laser import Laser
from copylot.hardware.orca_camera.camera import OrcaCamera


def align_tube_lens():
    # Start the camera
    camera = OrcaCamera()
    camera.run(nb_frame=-1)

    # Start the laser
    laser = Laser(wavelength="561", power=0.15)
    laser.turn_on()

    # Run till quit is requested
    print("type q to abort:")
    while input() != "q":
        sleep(1)

    # Follow the teardown needs
    laser.turn_off()
    camera.stop()


if __name__ == '__main__':
    align_tube_lens()
