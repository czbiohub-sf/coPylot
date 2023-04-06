import pytest
from unittest import mock

import serial

from copylot.hardware.lasers.vortran.vortran import VortranLaser


@pytest.fixture
def serial_number():
    '''
    The serial number of the mocked laser
    '''
    return 'some-serial-number'


@pytest.fixture
def mock_serial(mocker, serial_number):
    '''
    Mock the serial.Serial class and hard-code the raw lines returned by `readline`
    that are expected by VortranLaser._identify_laser
    '''
    mock_serial = mocker.patch("serial.Serial", autospec=True)
    mock_serial_instance = mock_serial.return_value

    # the value returned by calls to readline() during instantiation (i.e., in `_identify_laser`)
    mock_serial_instance.readline.return_value = (
        f"?LI={serial_number}, 600nm, 400mW, 500mW, laser-shape\r\n".encode()
    )
    # the `is_open` attribute is not found by autospec, so we manually define it
    mock_serial_instance.is_open = True

    return mock_serial


@pytest.fixture
def mock_ports(mocker):
    '''
    Mock the list_ports.comports function and return the list of ports
    '''
    mock_list_ports = mocker.patch("serial.tools.list_ports.comports", autospec=True)
    mock_ports = [mock.MagicMock(device=port) for port in ['some-port', 'another-port']]
    mock_list_ports.return_value = mock_ports
    return mock_ports


@pytest.fixture
def create_laser(mock_serial):
    '''
    Factory fixture to create a VortranLaser instance
    with mocked return values from one or more post-instantiation calls to `readline`
    (these calls are triggered by calls to the getters/setters)
    '''

    def _create_laser(readline_return_values):
        mock_serial.return_value.readline.side_effect = [
            mock_serial.return_value.readline.return_value,
            *[value.encode() for value in readline_return_values],
        ]
        laser = VortranLaser(port="some-port")
        return laser

    return _create_laser


def test_connect_with_serial_number(mock_serial, mock_ports, serial_number):
    '''
    if the user provides a serial number, available COM ports are tried
    until a laser is found that matches the provided serial number

    note: since we've mocked the serial.Serial().readline function,
    we know that the laser at the first port will match the serial_number
    '''
    laser = VortranLaser(serial_number=serial_number)

    mock_serial.assert_called_once_with(
        port=mock_ports[0],
        baudrate=laser.baudrate,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=laser.timeout,
    )
    assert laser.is_connected
    assert laser.serial_number == serial_number
    assert laser.address == mock_serial.return_value


@pytest.mark.usefixtures('mock_serial')
def test_connect_with_wrong_serial_number():
    '''
    if a serial number is provided, it must be correct or else the laser is not connected
    TODO: should this raise an exception?
    '''
    laser = VortranLaser(serial_number='obviously wrong serial number')
    assert not laser.is_connected


def test_connect_with_port(mock_serial, serial_number):
    '''
    if a port is provided, the serial number is only parsed and not checked/validated
    '''
    port = 'some-port'
    laser = VortranLaser(port=port)
    mock_serial.assert_called_once_with(
        port=port,
        baudrate=laser.baudrate,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=laser.timeout,
    )
    assert laser.is_connected
    assert laser.serial_number == serial_number
    assert laser.address == mock_serial.return_value


@pytest.mark.usefixtures('mock_serial', 'mock_ports')
def test_connect_with_no_args(serial_number):
    '''
    if no port or serial number is provided, then `get_lasers()` is called
    to obtain a list of available lasers, and the first laser in the list is connected to
    '''
    laser = VortranLaser()
    assert laser.is_connected
    assert laser.serial_number == serial_number


def test_disconnect(mock_serial):
    laser = VortranLaser(port='some-port')

    # call `disconnect` twice to check that subsequent calls have no effect
    laser.disconnect()
    laser.disconnect()
    mock_serial.return_value.close.assert_called_once()


@pytest.mark.usefixtures('mock_serial')
def test_get_lasers(mock_ports, serial_number):
    '''
    check that a laser is found for each mocked port
    '''
    laser_info = VortranLaser.get_lasers()
    for (laser_port, laser_serial_number), mock_port in zip(laser_info, mock_ports):
        assert laser_port == mock_port.device
        assert laser_serial_number == serial_number


def test_turn_laser_on_off(create_laser):
    laser = create_laser(['LE=1\r\n', 'LE=0\r\n'])
    assert laser.turn_on() == '1'
    assert laser.turn_off() == '0'


def test_set_get_power(create_laser):
    # note that the value returned by the second call to readline()
    # must be prefixed by the *query* '?LP' instead of the *command* 'LP'
    laser = create_laser(['LP=50\r\n', '?LP=50\r\n'])
    laser.laser_power = 50
    assert laser.laser_power == 50
