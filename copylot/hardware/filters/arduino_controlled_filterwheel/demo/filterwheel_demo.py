from copylot.hardware.filters.arduino_controlled_filterwheel.arduino_controlled_filterwheel import ArduinoControlledFilterWheel


if __name__ == '__main__':
    filterwheel = ArduinoControlledFilterWheel()

    filterwheel.set_position(2)
    filterwheel.set_position(3)
    filterwheel.set_position(4)
    filterwheel.set_position(5)
    filterwheel.set_position(0)
    filterwheel.set_position(1)
