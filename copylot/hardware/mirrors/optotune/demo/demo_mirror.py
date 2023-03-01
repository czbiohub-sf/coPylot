from time import sleep

import numpy

from copylot.hardware.mirrors.optotune.mirror import OptoMirror


def demo_mirror():
    mirror = OptoMirror()

    print(mirror.positions)

    del mirror


def demo_xy_scan():
    mirror = OptoMirror()

    for x in numpy.linspace(-0.2, 0.2, 200):
        mirror.position_x = x
        sleep(0.03)

    del mirror


def demo_spiral_scan():
    mirror = OptoMirror()

    theta = numpy.linspace(0, 20 * numpy.pi, 500)
    positions = []
    for theta in theta:
        r = theta * .005
        positions.append((r * numpy.cos(theta), r * numpy.sin(theta)))

    for position in positions:
        mirror.position_x = position[0]
        mirror.position_y = position[1]

    del mirror


if __name__ == '__main__':
    demo_mirror()
    demo_xy_scan()
    demo_spiral_scan()
