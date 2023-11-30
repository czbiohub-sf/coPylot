"""
@author:Yang Liu

Optotune Tip-tilt mirror controller MR-E-2 python wrapper

For more details regarding operation, refer to the manuals in https://www.optotune.com/fast-steering-mirrors

"""
from copylot import logger
from copylot.hardware.mirrors.optotune import optoMDC
from copylot.hardware.mirrors.abstract_mirror import AbstractMirror


class OptoMirror(AbstractMirror):
    def __init__(self, com_port: str = None):
        """
        Wrapper for Optotune mirror controller MR-E-2.
        establishes a connection through COM port

        """
        self.mirror = optoMDC.connect(
            com_port
            if com_port is not None
            else optoMDC.tools.list_comports.get_mre2_port()
        )

        self.channel_x = self.mirror.Mirror.Channel_0
        self.channel_x.SetControlMode(optoMDC.Units.XY)
        self.channel_x.StaticInput.SetAsInput()

        self.channel_y = self.mirror.Mirror.Channel_1
        self.channel_y.SetControlMode(optoMDC.Units.XY)
        self.channel_y.StaticInput.SetAsInput()
        logger.info("mirror connected")

    def __del__(self):
        self.position_x = 0
        self.position_y = 0
        self.mirror.disconnect()
        logger.info("mirror disconnected")

    @property
    def positions(self):
        """
        Returns
        -------
        float:
            Returning value is the current normalized angular value of the mirror
            value = theta/tan(50degree)
            50 degree is the maximum optical deflection angle for each direction.
        """
        return self.position_x, self.position_y

    @property
    def position_x(self):
        """
        Returns
        -------
        float:
            Returning value is the current normalized angular value of the mirror
            value = theta/tan(50degree)
            50 degree is the maximum optical deflection angle for each direction.

        """
        return self.channel_x.StaticInput.GetXY()[0]

    @position_x.setter
    def position_x(self, value):
        """
        Parameters
        ----------
        value:float
            The normalized angular value, value = theta/tan(50degree)
            50 degree is the maximum optical deflection angle for each direction.
            Here x has a range limits of [-1,1] , The combination of value for x-axis and y-axis should be less than 1
            (ex. x^2+y^1<1)
            when |x|<0.7 and |y| <0.7 any combination works. otherwise, one will be reduced to value to
            nearest edge of the unit circle
        """
        self.channel_x.StaticInput.SetXY(value)
        logger.info(f"position_x set to: {value}")

    @property
    def position_y(self):
        """
        Returns
        -------
        float:
            Returning value is the current normalized angular value of the mirror
            value = theta/tan(50degree)
            50 degree is the maximum optical deflection angle for each direction.
        """
        return self.channel_y.StaticInput.GetXY()[0]

    @position_y.setter
    def position_y(self, value):
        """
        Parameters
        ----------
        value(float):
            The normalized angular value, value = theta/tan(50degree)
            50 degree is the maximum optical deflection angle for each direction.
            Here x has a range limits of [-1,1] , The combination of value for x-axis and y-axis should be less than 1
            (ex. x^2+y^1<1)
            when |x|<0.7 and |y| <0.7 any combination works. otherwise, one will be reduced to value to
            nearest edge of the unit circle

        """
        self.channel_y.StaticInput.SetXY(value)
        logger.info(f"position_y set to: {value}")
