# %%
from copylot.hardware.stages.thorlabs.KIM001 import KCube_PiezoInertia
import time
from copylot import logger

from System import Decimal


# %%
def connect_to_stage():
    stage_1 = KCube_PiezoInertia(serial_number='74000001', simulator=True)
    stage_1.position = 5
    assert stage_1.position == 5
    stage_1.move_relative(10)
    assert stage_1.position == 15
    stage_1.move_relative(-30)
    assert stage_1.position == -15
    assert stage_1.travel_range == (None, None)
    stage_1.travel_range = (-100, 100)
    assert stage_1.travel_range == (-100, 100)
    stage_1.position = 200
    assert stage_1.position == 100


if __name__ == '__main__':
    connect_to_stage()
# %%
