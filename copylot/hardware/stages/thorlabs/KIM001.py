"""
Thorlabs KDC101 K-Cube for DC Motors wrapper

The user must install Thorlabs Kinesis and reference the appropriate paths below

For more details:
https://github.com/Thorlabs/Motion_Control_Examples/blob/main/Python/KCube/KIM101/kim101_pythonnet.py

"""
import os
import time
import sys
import clr
import os
from copylot import logger
from copylot.hardware.stages.abstract_stage import AbstractStage
import time
from typing import Dict
import numpy as np

clr.AddReference(
    "C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll"
)
clr.AddReference(
    "C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll"
)
clr.AddReference(
    "C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.KCube.InertialMotorCLI.dll"
)
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.KCube.InertialMotorCLI import *
from System import Decimal


class KCube_PiezoInertia(AbstractStage):
    CHANNEL_MAP: Dict[int, InertialMotorStatus.MotorChannels] = {
        1: InertialMotorStatus.MotorChannels.Channel1,
        2: InertialMotorStatus.MotorChannels.Channel2,
        3: InertialMotorStatus.MotorChannels.Channel3,
        4: InertialMotorStatus.MotorChannels.Channel4,
    }

    def __init__(
        self,
        serial_number: str = '74000001',
        channel: int = 1,
        stage_positive='forward',
        polling=False,
        simulator=False,
    ):
        self.serial_number = serial_number
        self.device = None
        self.device_name = None
        self.simulator = simulator
        self.timeout = 20000  # ms
        self.device_config = None
        self.device_settings = None
        self.stage_direction = stage_positive
        self.polling = polling
        self.channel = KCube_PiezoInertia.CHANNEL_MAP[channel]

        self.min_travel_range = None
        self.max_travel_range = None
        self.step_rate_val = 500
        self.step_acceleration_val = 1000

        if self.simulator:
            SimulationManager.Instance.InitializeSimulations()

        self.list_available_stages()
        self.connect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        logger.info("thorlabs stage disconnected")

    def list_available_stages(self):
        DeviceManagerCLI.BuildDeviceList()
        dev_list = DeviceManagerCLI.GetDeviceList()
        available_stages = [dev_list.get_Item(i) for i in range(dev_list.get_Count())]
        logger.info(f"Available stages: {available_stages}")
        return available_stages

    def load_configuration(self):
        self.device_config = self.device.GetInertialMotorConfiguration(
            self.serial_number
        )
        self.device_settings = ThorlabsInertialMotorSettings.GetSettings(
            self.device_config
        )
        self.update_configuration()

    def update_configuration(self):
        self.device_settings.Drive.Channel(self.channel).StepRate = self.step_rate_val
        self.device_settings.Drive.Channel(
            self.channel
        ).StepAcceleration = self.step_acceleration_val
        self.device.SetSettings(self.device_settings, True, True)

    def connect(self):
        if self._is_initialized():
            logger.info("Device is already initialized")
        else:
            logger.info(f"Initializing device with serial number {self.serial_number}")

            if self.serial_number is not None:
                self.device = KCubeInertialMotor.CreateKCubeInertialMotor(
                    self.serial_number
                )
                self.device.Connect(self.serial_number)
                # self.device_name = self.device
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
        # self.position = 0
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
        return self.device.GetPosition(self.channel)

    @position.setter
    def position(self, value: np.int32):
        # Check if position is within the set travel range
        if all((self.min_travel_range, self.max_travel_range)):
            if not self.min_travel_range <= value <= self.max_travel_range:
                raise RuntimeError('Position is outside of the stage travel range')

        self.device.MoveTo(self.channel, value, self.timeout)
        logger.info(f'Stage< {self.device_name} > reached position: {value}')

    @property
    def step_rate(self):
        return float(str(self.device_settings.Drive.Channel(self.channel).StepRate))

    @step_rate.setter
    def step_rate(self, value):
        self.step_rate_val = value
        self.update_configuration()

    @property
    def step_acceleration(self):
        return float(
            str(self.device_settings.Drive.Channel(self.channel).StepAcceleration)
        )

    @step_acceleration.setter
    def step_acceleration(self, value):
        self.step_acceleration_val = value
        self.update_configuration()

    def move_relative(self, offset):
        target_position = self.position + offset
        self.position = target_position

    def move_absolute(self, value: np.int32):
        self.position = value

    def home_device(self):
        return self.device.SetPositionAs(self.channel, 0)

    @property
    def travel_range(self):
        return (self.min_travel_range, self.max_travel_range)

    @travel_range.setter
    def travel_range(self, value):
        self.min_travel_range = value[0]
        self.max_travel_range = value[1]
        logger.info(
            f'Travel range set to ({self.min_travel_range}, {self.max_travel_range})'
        )
