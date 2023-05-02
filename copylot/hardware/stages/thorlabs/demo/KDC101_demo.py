#%%
from copylot.hardware.stages.thorlabs.KDC101 import KCube_DCServo
import time
from System import  Decimal
#%%

def connect_to_stage():
    stage_1 = KCube_DCServo('MT1-Z8', simulator=True)
    stage_1.position = 10
    assert stage_1.position == 10
    stage_1.disconnect()

if __name__ == '__main__':
    connect_to_stage()

# %%
stage_1 = KCube_DCServo('MT1-Z8', simulator=True)
stage_1.position = 10
#%%
value = 10
stage_1.device.get_Position()
# %%
