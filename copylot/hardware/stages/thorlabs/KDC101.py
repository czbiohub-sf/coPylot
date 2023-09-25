"""
Thorlabs KDC101 K-Cube for DC Motors wrapper

The user must install Thorlabs Kinesis and reference the appropriate paths below

For more details:
https://github.com/Thorlabs/Motion_Control_Examples/blob/main/Python/KCube/KDC101/kdc101_pythonnet.py

"""
import os
import time
import sys
import clr
import os
from copylot import logger
from copylot.hardware.stages.abstract_stage import AbstractStage
import time

clr.AddReference(
    "C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll"
)
clr.AddReference(
    "C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll"
)
clr.AddReference(
    "C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.KCube.DCServoCLI.dll"
)

from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.KCube.DCServoCLI import *
from System import Decimal


class KCube_DCServo(AbstractStage):
    def __init__(
        self,
        device_name,
        serial_number='27000001',
        stage_positive='forward',
        polling=False,
        simulator=False,
    ):
        self.serial_number = serial_number
        self.device = None
        self.device_name = device_name
        self.simulator = simulator
        self.timeout = 20000  # ms
        self.device_config = None
        self.stage_direction = stage_positive
        self.polling = polling
        self.max_travel_range = None
        self.min_travel_range = None

        if self.simulator:
            SimulationManager.Instance.InitializeSimulations()

        self.device_list()
        self.connect()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        logger.info("thorlabs stage disconnected")

    def list_available_stages(self):
        DeviceManagerCLI.BuildDeviceList()
        dev_list = DeviceManagerCLI.GetDeviceList()
        logger.info(f"Device List {dev_list}")
        return DeviceManagerCLI.GetDeviceList()

    def load_configuration(self):
        self.device_config = self.device.LoadMotorConfiguration(
            self.serial_number,
            DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings,
        )
        self.device_config.DeviceSettingsName = self.device_name
        self.device_config.UpdateCurrentConfiguration()
        self.device.SetSettings(self.device.MotorDeviceSettings, True, False)

    def connect(self):
        if self._is_initialized():
            logger.info("Device is already initialized")
        else:
            logger.info(f"Initializing device with serial number {self.serial_number}")

            if self.serial_number is not None:
                self.device = KCubeDCServo.CreateKCubeDCServo(self.serial_number)
                self.device.Connect(self.serial_number)
                time.sleep(0.25)
                if self.polling:
                    # Start polling and enable channel
                    # Polling blocks unless spawn the device in a separate thread
                    self.device.StartPolling(250)  # 250ms polling rate
                    time.sleep(25)
                self.device.EnableDevice()
                time.sleep(0.25)  # Wait for device to enable

                self.device_info()
                self._is_initialized()
                self.load_configuration()

    def _is_initialized(self):
        # Ensure that the device settings have been initialized
        if self.device is not None:
            if not self.device.IsSettingsInitialized():
                self.device.WaitForSettingsInitialized(10000)  # 10 second timeout
                assert self.device.IsSettingsInitialized() is True
        else:
            return False

    def device_info(self):
        # Get Device Information and display description
        device_info = self.device.GetDeviceInfo()
        logger.info(device_info.Description)
        return device_info.Description

    def zero_position(self):
        logger.info('Zeroing device')
        self.device.SetPositionAs(self.channel, 0)

    def close(self):
        # TODO: does it need to move back to a position?
        # self.position = 0.0
        if self.polling:
            self.device.StopPolling()
        self.device.Disconnect()

        if self.simulator:
            SimulationManager.Instance.UninitializeSimulations()

    def is_initialized(self):
        if not self.device.IsSettingsInitialized():
            self.device.WaitForSettingsInitialized(10000)  # 10 second timeout
            assert self.device.IsSettingsInitialized() is True

    def device_info(self):
        self.device_info = self.device.GetDeviceInfo()
        logger.info(self.device_info.Description)

    @property
    def position(self):
        return float(str(self.device.Position))

    @position.setter
    def position(self, value):
        if self.min_travel_range and self.max_travel_range is not None:
            if value > self.max_travel_range:
                value = self.max_travel_range
            if value < self.min_travel_range:
                value = self.min_travel_range
        value = Decimal(value)
        self.device.MoveTo(value, self.timeout)
        time.sleep(1)
        logger.info(f'Stage< {self.device_name} > reached position: {value}')

    def move_relative(self, value):
        abs_value = abs(value)
        if self.stage_direction == 'forward':
            if value > 0:
                (MotorDirection.Forward, Decimal(abs_value), self.timeout)
            else:
                (MotorDirection.Backward, Decimal(abs_value), self.timeout)
        else:
            if value > 0:
                (MotorDirection.Backward, Decimal(abs_value), self.timeout)
            else:
                (MotorDirection.Forward, Decimal(abs_value), self.timeout)

    def move_relative_2(self, value):
        target_position = self.position + value
        self.position = target_position

    def move_absolute(self, value):
        self.position = value

    def home_device(self):
        return self.device.Home(60000)

    @property
    def travel_range(self):
        return (self.min_travel_range, self.max_travel_range)

    @travel_range.setter
    def travel_range(self, value):
        self.max_travel_range = value[0]
        self.min_travel_range = value[1]
