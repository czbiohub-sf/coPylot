from copylot.hardware.asi_stage.stage import ASIStage


def zero_home_demo():
    stage = ASIStage()
    stage.zero()

    # TODO: move the stage somewhere else
    # stage.

    stage.zero()


if __name__ == '__main__':
    zero_home_demo()
