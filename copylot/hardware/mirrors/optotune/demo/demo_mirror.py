from copylot.hardware.mirrors.optotune.mirror import OptoMirror


def demo_mirror():
    mirror = OptoMirror()

    print(mirror.positions)

    del mirror

def demo_xy_scan():
    mirror = OptoMirror()

    print(mirror.positions)

    del mirror


if __name__ == '__main__':
    demo_mirror()
