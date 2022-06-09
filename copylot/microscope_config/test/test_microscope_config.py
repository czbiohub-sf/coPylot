import pathlib

from copylot.microscope_config.microscope_config import MicroscopeConfig


def test_read_config():
    config_path = pathlib.Path("copylot/microscope_config/configs/daxi.yaml").resolve()
    scope_config = MicroscopeConfig.read_config(config_path)

    assert scope_config.name == "daxi"
    assert scope_config.nb_devices == 14
