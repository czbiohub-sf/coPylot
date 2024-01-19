# %%
from copylot.assemblies.photom.photom import PhotomAssembly
from copylot.assemblies.photom.utils import affine_transform
from copylot.hardware.mirrors.optotune.mirror import OptoMirror
from copylot.assemblies.photom.photom_mock_devices import MockLaser, MockMirror
import time

# %%
# Mock imports for the mirror and the lasers
laser = MockLaser('Mock Laser', power=0)
mirror = OptoMirror(com_port='COM8')

# %%
# Test the moving of the mirrors
mirror.position = (0.009, 0.0090)
time.sleep(1)
mirror.position = (0.000, 0.000)

curr_pos = photom_device.get_position(mirror_index=0)
print(curr_pos)
assert curr_pos == (0.000, 0.000)
# %%
## Test using the photom_device
camera_sensor_width = 1280
camera_sensor_height = 1280

photom_device = PhotomAssembly(
    laser=[laser],
    mirror=[mirror],
    affine_matrix_path=[
        r'C:\Users\ZebraPhysics\Documents\GitHub\coPylot\copylot\assemblies\photom\demo\test_tmp.yml'
    ],
)
photom_device.set_position(
    mirror_index=0, position=[camera_sensor_width // 2, camera_sensor_height // 2]
)
curr_pos = photom_device.get_position(mirror_index=0)
print(curr_pos)


# %%
# TODO: Test the calibration without GUI
import time

start_time = time.time()
photom_device._calibrating = True
while time.time() - start_time < 5:
    # Your code here
    elapsed_time = time.time() - start_time
    print(f'starttime: {start_time} elapsed_time: {elapsed_time}')
    photom_device.calibrate(
        mirror_index=0, rectangle_size_xy=[0.002, 0.002], center=[0.000, 0.000]
    )
photom_device._calibrating = False

# %%
