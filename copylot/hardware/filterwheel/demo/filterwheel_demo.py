import time

from copylot.hardware.filterwheel.filterwheel import FilterWheel

filterwheel = FilterWheel()

time.sleep(2)

filterwheel.set_position(2)
filterwheel.set_position(3)
filterwheel.set_position(4)
filterwheel.set_position(5)
filterwheel.set_position(0)
filterwheel.set_position(1)

