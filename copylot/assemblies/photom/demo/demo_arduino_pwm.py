# %%
from copylot.assemblies.photom.utilis.arduino_pwm import ArduinoPWM

# TODO: modify COM port based on the system
arduino = ArduinoPWM(serial_port='COM3', baud_rate=115200)

# %%
# Test the PWM signal
duty_cycle = 50  # [%] (0-100)
milliseconds_on = 10  # [ms]
frequency = 1 / (milliseconds_on * 1000)  # [Hz]
total_duration = 5000  # [ms] total time to run the PWM signal

command = f'U,{duty_cycle},{frequency},{total_duration}'
arduino.send_command(command)
arduino.send_command('S')


# %%
# Run it every 5 seconds
import time

repetitions = 10
time_interval_s = 5

for i in range(repetitions):
    arduino.send_command('S')
    time.sleep(time_interval_s)
