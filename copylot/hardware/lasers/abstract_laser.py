from abs import ABCMeta, abstractmethod


class AbstractLaser(metaclass=ABCMeta):
    _device_id = None

    @property
    def device_id(self):
        return self._device_id

    @property
    @abstractmethod
    def is_conencted(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def control_mode(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def external_power_control(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def current_control(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def toggle_emission(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def laser_power(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def pulse_power(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def pulse_mode(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def maximum_power(self):
        raise NotImplementedError()

    @property
    @abstractmethod
    def status(self):
        raise NotImplementedError()
