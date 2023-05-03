#%%
from copylot.hardware.stages.thorlabs.KIM001 import KCube_PiezoInertia
import time
from System import  Decimal
#%%
def connect_to_stage():
    stage_1 = KCube_PiezoInertia(serial_number='74000001', simulator=True)
    stage_1.position = 5
    assert stage_1.position == 5
        
if __name__ == '__main__':
    connect_to_stage()