from time import sleep

from copylot.hardware.galvo.galvo import Galvo


def demo_move_galvo():
    galvo = Galvo()

    for _ in range(6):
        galvo.set_position(15 * _)
        sleep(1)
        galvo.zero()


if __name__ == '__main__':
    demo_move_galvo()
