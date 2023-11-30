from abc import ABCMeta, abstractmethod
from typing import Tuple


class AbstractMirror(metaclass=ABCMeta):
    """AbstractMirror

    This class includes only the members that known to be common
    across different mirror adapters. By no
    means this class in a final state. We will be making additions
    as needs rise.

    """

    def __init__(self):
        self.affine_transform_obj = None

    @property
    @abstractmethod
    def position(self) -> Tuple[float, float]:
        """Get the current mirror position"""
        pass

    @position.setter
    @abstractmethod
    def position(self, value: Tuple[float, float]):
        """Set the mirror position"""
        pass

    @property
    @abstractmethod
    def relative_position(self) -> Tuple[float, float]:
        """Get the current relative mirror position"""
        pass

    @relative_position.setter
    @abstractmethod
    def relative_position(self, value: Tuple[float, float]):
        """Set the relative mirror position"""
        pass

    @property
    @abstractmethod
    def movement_limits(self) -> Tuple[float, float, float, float]:
        """Get the current mirror movement limits"""
        pass

    @movement_limits.setter
    @abstractmethod
    def movement_limits(self, value: Tuple[float, float, float, float]):
        """Set the mirror movement limits"""
        pass

    @property
    @abstractmethod
    def step_resolution(self) -> float:
        """Get the current mirror step resolution"""
        pass

    @step_resolution.setter
    @abstractmethod
    def step_resolution(self, value: float):
        """Set the mirror step resolution"""
        pass

    @abstractmethod
    def set_home(self):
        """Set the mirror home position"""
        pass

    @abstractmethod
    def set_origin(self, axis: str):
        """Set the mirror origin for a specific axis"""
        pass

    @property
    @abstractmethod
    def external_drive_control(self) -> str:
        """Get the current mirror drive mode"""
        pass

    @external_drive_control.setter
    @abstractmethod
    def external_drive_control(self, value: bool):
        """Set the mirror drive mode"""
        pass

    @abstractmethod
    def voltage_to_position(self, voltage: Tuple[float, float]) -> Tuple[float, float]:
        """Convert voltage to position"""
        pass
