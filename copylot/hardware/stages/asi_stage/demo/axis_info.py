from copylot.hardware.stages.asi_stage.stage import ASIStage


def info_demo():
    stage = ASIStage()
    stage.info("X")
    print("======")
    stage.info("Y")


if __name__ == '__main__':
    info_demo()
