from copylot.hardware.lights.voltran import voltran


if __name__ == 'main_':
    voltran.get_lasers()
    laser = voltran.VoltranLaser()
    power = laser.get_power()