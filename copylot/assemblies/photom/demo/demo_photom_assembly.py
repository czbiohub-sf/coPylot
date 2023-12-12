
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
photom_device.calibrate(mirror_index=0, rectangle_size_xy=(0.01, 0.01))

# %%
