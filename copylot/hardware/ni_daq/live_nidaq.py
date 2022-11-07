import nidaqmx


class LiveNIDaq:
    def __init__(self):
        self._active_ao_channels = set()
        self._active_do_channels = set()

    def __del__(self):
        self.zero()

    @property
    def active_ao_channels(self):
        """List of active analog channels"""
        return self._active_ao_channels

    def add_active_ao_channel(self, channel):
        self._active_ao_channels.add(channel)

    @property
    def active_do_channels(self):
        return self._active_do_channels

    def add_active_do_channel(self, channel):
        self._active_do_channels.add(channel)

    def zero(self):
        for channel in self.active_ao_channels:
            with nidaqmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan(channel)
                task.write([0.0], auto_start=True)

    def set_constant_ao_voltage(self, channel: str, voltage: float):
        """
        Sets a given voltage to the given channel.

        Parameters
        ----------
        channel : str
        voltage : float

        """
        if channel in self.active_ao_channels:
            with nidaqmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan(channel)
                task.write([voltage], auto_start=True)
        else:
            raise ValueError(
                "Constant voltage can not be set to an inactive analog channel."
            )
