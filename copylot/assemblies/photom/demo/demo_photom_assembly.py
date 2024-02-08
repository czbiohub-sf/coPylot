# %%
from copylot.assemblies.photom.photom import PhotomAssembly
from copylot.assemblies.photom.utils import affine_transform
from copylot.hardware.mirrors.optotune.mirror import OptoMirror
from copylot.assemblies.photom.photom_mock_devices import MockLaser, MockMirror
from copylot.hardware.cameras.flir.flir_camera import FlirCamera
import time

# %%
config_file = './photom_VIS_config.yml'
# Mock imports for the mirror and the lasers
laser = MockLaser(name='Mock Laser', power=0)
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
    camera=[camera],
)
photom_device.set_position(
    mirror_index=0, position=[camera_sensor_width // 2, camera_sensor_height // 2]
)
curr_pos = photom_device.get_position(mirror_index=0)
print(curr_pos)

# %%
from copylot.assemblies.photom.utils.scanning_algorithms import (
    calculate_rectangle_corners,
    generate_grid_points,
)
import time

# mirror_roi = [
#     [-0.005, 0.018],  # [y,x]
#     [0.013, 0.0],
# ]
mirror_roi = [[0.18, -0.005], [0.0, 0.013]]
grid_points = generate_grid_points(rectangle_size=mirror_roi, n_points=5)
for idx, coord in enumerate(grid_points):
    mirror.position = [coord[0], coord[1]]
    print(coord)
    time.sleep(0.5)


# %%
cam = FlirCamera()
# open the system
cam.open()
# serial number
print(cam.device_id)
# list of cameras
print(cam.list_available_cameras())
photom_device = PhotomAssembly(
    laser=[laser],
    mirror=[mirror],
    affine_matrix_path=[r'./affine_T.yml'],
    camera=[cam],
)
# %%
mirror_roi = [
    [-0.005, 0.018],  # [y,x]
    [0.013, 0.0],
]  # Top-left and Bottom-right corners of the mirror ROI
photom_device.camera[0].exposure = 5000
photom_device.camera[0].gain = 0
photom_device.camera[0].flip_horizontal = True
photom_device.camera[0].pixel_format = 'Mono16'
photom_device.calibrate_w_camera(
    mirror_index=0,
    camera_index=0,
    rectangle_boundaries=mirror_roi,
    grid_n_points=5,
    config_file='./affine_T.yaml',
    save_calib_stack_path='./calib_stack',
)

# %%
# # TODO: Test the calibration without GUI
# import time

# start_time = time.time()
# photom_device._calibrating = True
# while time.time() - start_time < 5:
#     # Your code here
#     elapsed_time = time.time() - start_time
#     print(f'starttime: {start_time} elapsed_time: {elapsed_time}')
#     photom_device.calibrate(
#         mirror_index=0, rectangle_size_xy=[0.002, 0.002], center=[0.000, 0.000]
#     )
# photom_device._calibrating = False

# %%
