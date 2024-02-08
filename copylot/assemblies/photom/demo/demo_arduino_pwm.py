# %%
from copylot.assemblies.photom.photom import PhotomAssembly
from copylot.assemblies.photom.utils import affine_transform
from copylot.hardware.mirrors.optotune.mirror import OptoMirror
from copylot.assemblies.photom.photom_mock_devices import MockLaser, MockMirror
from copylot.hardware.cameras.flir.flir_camera import FlirCamera
import time
from copylot.assemblies.photom.utilis.arduino_pwm import ArduinoPWM

# %%
config_file = './photom_VIS_config.yml'
# Mock imports for the mirror and the lasers
laser = MockLaser('Mock Laser', power=0)
mirror = OptoMirror(com_port='COM8')
cam = FlirCamera()
cam.open()

# TODO: modify COM port based on the system
arduino = ArduinoPWM(serial_port='COM3', baud_rate=115200)

# %%
# Make the photom device
photom_device = PhotomAssembly(
    laser=[laser],
    mirror=[mirror],
    affine_matrix_path=[r'./affine_T.yml'],
    camera=[cam],
)

# %%
# Perform calibration
mirror_roi = [
    [-0.01, 0.00],
    [0.019, 0.019],
]  # Top-left and Bottom-right corners of the mirror ROI
photom_device.camera[0].exposure = 5000  # [us]
photom_device.camera[0].gain = 0
# photom_device.camera[0].flip_horizontal = True
# photom_device.camera[0].pixel_format = 'Mono16'
photom_device.calibrate_w_camera(
    mirror_index=0,
    camera_index=0,
    rectangle_boundaries=mirror_roi,
    grid_n_points=5,
    config_file='./affine_T.yaml',
    save_calib_stack_path='./calib_stack',
)
# %%
# Set the ablation parameters
# Test the PWM signal
duty_cycle = 50  # [%] (0-100)
milliseconds_on = 10  # [ms]
total_duration = 5000  # [ms] total time to run the PWM signal

# %%
# Ablate the cells
frequency = 1 / (milliseconds_on * 1000)  # [Hz]
arduino.set_pwm(duty_cycle, frequency, total_duration)
arduino.start_timelapse(repetitions=3, time_interval_s=5)
