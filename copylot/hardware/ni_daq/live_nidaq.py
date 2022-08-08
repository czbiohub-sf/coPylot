import nidaqmx


class LiveNIDaq:
    def __init__(self):
        self._active_analog_channels = []

    @property
    def active_analog_channels(self):
        """
        List of active analog channels
        """
        return self._active_analog_channels

    @active_analog_channels.setter
    def active_analog_channels(self, channel):
        self._active_analog_channels.append(channel)

    def zero(self):
        for channel in self.active_analog_channels:
            with nidaqmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan(channel)
                task.write([0], auto_start=True)

    def set_constant_voltage(self, channel, voltage):
        """
        Sets a given voltage to the given channel.

        Parameters
        ----------
        channel
        voltage

        """
        if channel in self.active_analog_channels:
            with nidaqmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan(channel)
                task.write([voltage], auto_start=True)
        else:
            raise ValueError("Constant voltage can not be set to an inactive analog channel.")
