from copylot.microscope_config.microscope_config import read_config


def test_read_config():
    config_path = "copylot/microscope_config/configs/daxi.yaml"
    scope_config = read_config(config_path)

    assert scope_config.name == "daxi"
    assert scope_config.nb_devices == 4
