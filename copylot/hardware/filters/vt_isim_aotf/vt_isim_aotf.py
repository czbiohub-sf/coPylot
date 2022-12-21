from enum import Enum


class AOTF_MODES(Enum):
    VTI_AOTF_MANUAL = 0
    VTI_AOTF_SOFTWARE = 1


class AOTF:
    """AOTF

    Parameters
    ----------
    channel_names : tuple

    """

    def __init__(
            self,
            channel_names: tuple = (),
    ):
        self.shutter_on = False
        self.channel_names = channel_names
        self.channel_power_status = {
            channel_name: False for channel_name in channel_names
        }

    def __del__(self):
        raise NotImplementedError()

    def set_intensity(self, channel_name: str, intensity: int):
        if channel_name not in self.channel_names:
            raise ValueError(f"Channel: {channel_name} is not a valid option...")

        if intensity < 0 or intensity > 100:
            raise ValueError(f"Intensity has to be between [0,100], {intensity} is invalid...")

        # Make a call to vti_SetIntensity()
        raise NotImplementedError()

    def set_channel_power_status(self, channel_name: str, power: bool = False):
        if channel_name in self.channel_names:
            self.channel_power_status[channel_name] = power

            # Make a call to vti_SetTTLBitmask()
        else:
            raise ValueError(f"No channel exist with given {channel_name}...")

    def toggle_shutter(self):
        # Make a call to vti_SetShutter()
        raise NotImplementedError()
