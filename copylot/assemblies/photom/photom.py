from dataclasses import dataclass


class photom:
    def __init__(self, camera, laser, mirror, dac):
        self.camera = camera
        self.laser = laser
        self.mirror = mirror
        self.DAC = dac

    ## Camera Functions
    def capture(self):
        pass

    ## Mirror Functions
    def move_mirror(self):
        pass

    ## LASER Fucntions
    def change_laser_power(self):
        pass
