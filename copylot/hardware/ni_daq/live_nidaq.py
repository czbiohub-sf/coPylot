import nidaqmx


class LiveNIDaq:
    def __init__(self):
        pass

    def zero(self):
        raise NotImplementedError

    def set_constant_voltage(self, channel, voltage):
        """

        Parameters
        ----------
        channel
        voltage

        """
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan(channel)
            task.write([voltage], auto_start=True)
