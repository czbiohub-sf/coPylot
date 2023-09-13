# %%
from copylot.hardware.lasers.vortran.vortran import VortranLaser
import time


def demo_get_laser_list():
    """
    Get the Voltran Lasers Connected to the system
    """
    laser_list = VortranLaser.get_lasers()
    print(laser_list)


def demo_set_power():
    """
    Test Setting the power of the laser.
    To read the value, emission = 1
    """
    power = 3.0
    laser_list = VortranLaser.get_lasers()
    laser = VortranLaser(port=laser_list[0][0])
    laser.toggle_emission = 1
    laser.laser_power = 2.0
    assert (laser.laser_power - power) < (power * 0.2)
    power = float(5.0)
    laser.laser_power = power
    assert (laser.laser_power - power) < (power * 0.2)
    laser.toggle_emission = 0
    laser.disconnect()


def demo_toggle_emission():
    """
    Test toggling the emission
    """
    laser_list = VortranLaser.get_lasers()
    laser = VortranLaser(port=laser_list[0][0])
    laser.emission_delay = 0
    laser.laser_power = 2.0
    laser.toggle_emission = 1
    time.sleep(3)
    laser.toggle_emission = 0
    laser.disconnect()


if __name__ == '__main__':
    demo_get_laser_list()
    demo_toggle_emission()
    demo_set_power()
