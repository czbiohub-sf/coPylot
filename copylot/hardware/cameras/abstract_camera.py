from abc import ABCMeta, abstractmethod


class AbstractCamera(metaclass=ABCMeta):

    @abstractmethod
    def snap(self):
        """Method to capture a single image from the camera."""
        raise NotImplementedError()

    @abstractmethod
    def list_available_cameras(self):
        """List all cameras that driver discovers."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def exposure(self):
        raise NotImplementedError()

    @exposure.setter
    @abstractmethod
    def exposure(self, value):
        raise NotImplementedError()

    @property
    @abstractmethod
    def exposure_limits(self):
        """
        Valid minimum and maximum exposure values.

        Returns
        -------
        Tuple
            (min_valid_exposure, max_valid_exposure)
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def bitdepth(self):
        raise NotImplementedError()

    @bitdepth.setter
    @abstractmethod
    def bitdepth(self, value):
        raise NotImplementedError()

    @property
    @abstractmethod
    def image_size(self):
        raise NotImplementedError()

    @image_size.setter
    @abstractmethod
    def image_size(self, value):
        raise NotImplementedError()

    @property
    @abstractmethod
    def image_size_limits(self):
        """
        Valid minimum and maximum image_size values.

        Returns
        -------
        Tuple
            (min_image_width, max_image_width, min_image_height, max_image_height)
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def binning(self):
        raise NotImplementedError()

    @binning.setter
    @abstractmethod
    def binning(self, value):
        raise NotImplementedError()

    @property
    @abstractmethod
    def gain(self):
        raise NotImplementedError()

    @gain.setter
    @abstractmethod
    def gain(self, value):
        raise NotImplementedError()

    @property
    @abstractmethod
    def gain_limits(self):
        """
        Valid minimum and maximum gain values.

        Returns
        -------
        Tuple
            (min_valid_gain, max_valid_gain)
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def shutter_mode(self):
        raise NotImplementedError()

    @shutter_mode.setter
    @abstractmethod
    def shutter_mode(self, mode):
        raise NotImplementedError()
