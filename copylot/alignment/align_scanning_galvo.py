from time import sleep


def align_scanning_galvo():
    laser = Laser()
    scanning_galvo = Galvo()
    gamma_galvo = Galvo("gamma")
    beta_galvo = Galvo("beta")

    scanning_galvo.set_minimum(0)
    scanning_galvo.set_maximum(45)
    scanning_galvo.set_speed(1)

    gamma_galvo.set_position(30)
    beta_galvo.set_position(45)

    laser.turn_on()

    print("type q to abort:")
    while input() != "q":
        scanning_galvo.scan()
        sleep(1)

    laser.turn_off()


if __name__ == '__main__':
    align_scanning_galvo()
