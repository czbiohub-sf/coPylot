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
    CHANNEL_MAP : Dict [int, InertialMotorStatus.MotorChannels] = {
        1: InertialMotorStatus.MotorChannels.Channel1,
        2: InertialMotorStatus.MotorChannels.Channel2,
        3: InertialMotorStatus.MotorChannels.Channel3,
        4: InertialMotorStatus.MotorChannels.Channel4
    }

    def __init__(self, serial_number:str ='74000001', channel:int = 1, stage_positive = 'forward', polling = False, simulator=False):
        self.serial_number = serial_number
        self.device = None
        self.device_name = None
        self.simulator = simulator
        self.timeout = 20000  #ms
        self.device_config = None
        self.device_settings = None
        self.stage_direction = stage_positive
        self.polling = polling
        self.channel = KCube_PiezoInertia.CHANNEL_MAP[channel]

        if self.simulator:
            SimulationManager.Instance.InitializeSimulations()

        self.device_list()
        self.connect()

    def __del__(self):
        self.disconnect()
        logger.info("thorlabs stage disconnected")

    def device_list(self):
        DeviceManagerCLI.BuildDeviceList()
        dev_list = DeviceManagerCLI.GetDeviceList()
        logger.info(f"Device List {dev_list}")
        return DeviceManagerCLI.GetDeviceList()

    def load_configuration(self):
        self.device_config = self.device.GetInertialMotorConfiguration(self.serial_number)
        self.device_settings = ThorlabsInertialMotorSettings.GetSettings(self.device_config)
        #Default Settings
        self.device_settings.Drive.Channel(self.channel).StepRate = 1000
        self.device_settings.Drive.Channel(self.channel).StepAcceleration = 100000
        self.device.SetSettings(self.device_settings, True, True)

    def connect(self):
        if self._is_initialized():
            logger.info("Device is already initialized")
        else:
            logger.info(f"Initializing device with serial number {self.serial_number}")

            if self.serial_number is not None:
                self.device = KCubeInertialMotor.CreateKCubeInertialMotor(self.serial_number)
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

    def disconnect(self):
        # TODO: does it need to move back to a position?
        self.position = 0
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
    def position(self, value : np.int32):
        self.device.MoveTo(self.channel, value, self.timeout)
        time.sleep(1)
        logger.info(f'Stage< {self.device_name} > reached position: {value}')

    @property
    def step_rate(self):
        return float(str(self.device_settings.Drive.Channel(self.channel).StepRate))
    
    @step_rate.setter
    def step_rate(self, value):
        self.device_settings.Drive.Channel(self.channel).StepRate = value
    
    @property
    def step_acceleration(self):
        return float(str(self.device_settings.Drive.Channel(self.channel).StepAcceleration))
    
    @step_acceleration.setter
    def step_acceleration(self, value):
        self.device_settings.Drive.Channel(self.channel).StepAcceleration = value
    
    def move_relative(self,value):
        curr_position = self.position
        target_position = curr_position + value
        if target_position < 0:
            logger.warning('Stage out of range')
        else:
            self.position  = target_position

    def home_device(self):
       return self.device.SetPositionAs(self.channel, 0)

