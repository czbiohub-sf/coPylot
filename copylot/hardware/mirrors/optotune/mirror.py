from copylot.hardware.mirrors.optotune import optoMDC


class OptoMirror:
    def __init__(self, com_port: str = None):
        self.mirror = optoMDC.connect(
            com_port if com_port is not None else "COM3"
        )

        self.channel_x = self.mirror.Mirror.Channel_0
        self.channel_x.SetControlMode(optoMDC.Units.XY)
        self.channel_x.StaticInput.SetAsInput()

        self.channel_y = self.mirror.Mirror.Channel_1
        self.channel_y.SetControlMode(optoMDC.Units.XY)
        self.channel_y.StaticInput.SetAsInput()
        print("mirror connected")

    def __del__(self):
        self.mirror.disconnect()
        print("mirror disconnected")

    @property
    def positions(self):
        return self.position_x, self.position_y

    @property
    def position_x(self):
        """

        Returns
        -------

        """
        return self.channel_x.StaticInput.GetXY()[0]

    @position_x.setter
    def position_x(self, value):
        """

        Parameters
        ----------
        value

        """
        self.channel_x.StaticInput.SetXY(value)
        print(f"position_x set to: {value}")

    @property
    def position_y(self):
        return self.channel_y.StaticInput.GetXY()[0]

    @position_y.setter
    def position_y(self, value):
        self.channel_y.StaticInput.SetXY(value)
        print(f"position_y set to: {value}")
