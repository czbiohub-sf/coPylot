from time import sleep

from copylot.hardware.laser.laser import Laser


def demo_laser_power():
    laser = Laser()

    for _ in range(5):
        laser.set_power(0.01 * _)
        laser.turn_on()
        sleep(1)
        laser.turn_off()


if __name__ == '__main__':
    demo_laser_power()
