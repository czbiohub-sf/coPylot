from copylot.hardware.asi_stage.stage import ASIStage, ASIStageScanMode


def zero_home_demo():
    stage = ASIStage()
    stage.zero()

    # TODO: move the stage somewhere else
    # stage.

    stage.zero()


def raster_scan_demo():
    stage = ASIStage()
    stage.zero()

    stage.set_scan_mode(mode=ASIStageScanMode.RASTER)

    stage.start_scan()

    stage.zero()


# def serpentine_scan_demo():
#     stage = ASIStage()
#     stage.zero()
#
#     stage.set_scan_mode(mode=ASIStageScanMode.SERPENTINE)
#
#     stage.start_scan()
#
#     stage.zero()


if __name__ == '__main__':
    # zero_home_demo()

    raster_scan_demo()

    # serpentine_scan_demo()
