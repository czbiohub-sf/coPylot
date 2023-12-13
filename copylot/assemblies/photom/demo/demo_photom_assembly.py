
#%%
from copylot.assemblies.photom.photom import PhotomAssembly
from copylot.hardware.mirrors.optotune.mirror import OptoMirror
from copylot.assemblies.photom.photom_mock_devices import MockLaser, MockMirror

#%%

laser = MockLaser('Mock Laser', power=0)
mirror = OptoMirror(com_port='COM8')

#%%
mirror.position = (0.009,0.0090)
# %%
mirror.position = (0.000,0.000)

# %%
photom_device = PhotomAssembly(laser=[laser], mirror=[mirror], 
                               affine_matrix_path=[r'C:\Users\ZebraPhysics\Documents\GitHub\coPylot\copylot\assemblies\photom\demo\affine_T.yml'],
                               )
# %%
photom_device?
# %%

curr_pos = photom_device.get_position(mirror_index=0)
print(curr_pos)
#%%
photom_device.set_position(mirror_index=0,position=[0.009,0.009])
curr_pos = photom_device.get_position(mirror_index=0)
print(curr_pos)

# %%
import time
start_time = time.time()
center = 0.009
photom_device._calibrating = True
while time.time() - start_time < 5:
    # Your code here
    elapsed_time = time.time() - start_time
    print(f'starttime: {start_time} elapsed_time: {elapsed_time}')
    photom_device.calibrate(mirror_index=0, rectangle_size_xy=[0.002, 0.002], center=[0.000,0.000])
photom_device._calibrating = False

# %%
