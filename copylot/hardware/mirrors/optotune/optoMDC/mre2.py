# -*- coding: utf-8 -*-
from .registers import mre2_registers as Registers
from .tools.list_comports import get_mre2_port
# from ._connections import Board as _Board, Channel as _Channel, ProxyBoard as _ProxyBoard
from .optoKummenberg.connections import Board as _Board, Channel as _Channel, ProxyBoard as _ProxyBoard
"""MR-E-2 SDK.

The MRE2 SDK is organized in the following way:

         Board.Mirror.Channel.System.RegisterCommand(parameters)

  Board:      Low/mid level object for operating the firmware (vector patterns, simple/pro commands, etc)
  Mirror:     Handles Proxy Mirror Board Operations (GetTemperature, GetConnectedStatus, etc)
  Channel:    A given channel, which can set input types, gain, etc.
  System:     Each channel has its own stages. From here can perform commands that get/set individual registers.
  registers:  Each system has several registers, which are dictionaries with elements regarding valid units/range.


To begin:
Import necessary module and initialize a board (verbose for console output)

>>>from mre2 import MRE2Board
>>>mre2 = MRE2Board(port='COM12', verbose=True)  # this will connect and synchronize all channel with the firmware

Define the system you want to interact with (board.mirror.channel.system) (see registers.system_names for a list)
>>>sig_gen = mre2.Mirror.Channel_0.SignalGenerator
Start setting individual registers
>>>sig_gen.SetAmplitude(0.1)

Additional operations are available directly through the Board object (get/set multiple, reset, etc)
For example, multiple set/get can be done. After this, the system will output a sinusoid on channel 0.
>>>mre2.set_value([sig_gen.frequency, sig_gen.amplitude, sig_gen.unit, sig_gen.run], [10.0, 0.1, Units.CURRENT, 1])
>>>mre2.get_value([sig_gen.frequency, sig_gen.amplitude, sig_gen.unit, sig_gen.run])

Example
-------
More examples to come...
"""

hwid = '0483:A31E'
"""str: default hardware id of mre2 board, for port recognition.
"""


# standard MRE2 Board
class MRE2Board(_Board):
    r"""
    Board object from which to issue MRE2 commands over a serial connection.

    Parameters
    ----------
    port, baudrate, comm_lock, timeout, verbose
        Standard serial connection parameters. Extended from Connection class.
    boot_in_simple: bool, optional = False
        Determines whether or not Board will be set in simple-mode after initialization.
    board_reset: bool, optional = False
        Determines whether or not to reset the Board during initialization.

    Raises
    ------
    none

    Notes
    -----
    Board extends Connection class. Refer to Connection for methods, parameters, etc.
    Board inherits Commands. Refer to Commands for methods, parameters, etc.

    Examples
    --------
    Instantiate a simple-mode Board with connection over COM12 port, with baud rate 9600. Then switch into pro-mode.
    This will not flush the firmware registers, so it is assumed to already be reset.

    >>> board = MRE2Board(port='COM12', baudrate=9600, verbose=True, simple=True)
    Establishing Connection via port [COM12]...
    Connected.
    Initializing Board in Simple Mode...
    Sending: b'~\x00\x06\x02\x00\x00\x00\x00~'
    Received: b''
    Verifying Simple via Handshake...
    Sending: b'Start\r\n'
    Received: b'NO\r\n'
    Handshake NOT Successful: UNKNOWN_ERROR_CODE.
    Sending: b'Start\r\n'
    Received: b'OK\r\n'
    Handshake Successful.
    Board Initialized in Simple Mode.
    Initialization Finalized. Board is Ready.
    >>> board.go_pro()
    Sending: b'GoPro\r\n'
    Received: b'OK\r\n'
    Go Pro Successful.

    """
    def __init__(self, port: str = None, baudrate: int = 115200, comm_lock: bool = True,
                 timeout: float = 2, verbose: bool = False, boot_in_simple: bool = False,
                 board_reset: bool = False, inter_byte_timeout: float = 0.2):
        if port is None:
            try:
                port = get_mre2_port()
            except IndexError:
                print("MRE2 Device Not Found. Check Connection.")

        _Board.__init__(self, port=port, baudrate=baudrate, comm_lock=comm_lock,
                        timeout=timeout, verbose=verbose, simple=boot_in_simple,
                        board_reset=board_reset, inter_byte_timeout=inter_byte_timeout)

        # board-level systems
        self.VectorPatternMemory = Registers.VectorPatternMemory(board=self)
        self.TemperatureManager = Registers.TemperatureManager(board=self)
        self.MISC = Registers.Misc(board=self)
        self.Logger = Registers.Logger(board=self)
        # mirror proxy board
        del self.ProxyBoard
        self.Mirror = MRE2Mirror(board=self)
        self.channel = [self.Mirror.Channel_0, self.Mirror.Channel_1]
        self.systems = Registers.systems()
        if self.verbose:
            print('Initialization Finalized, Board is Ready.')


class MRE2Mirror(_ProxyBoard):
    r"""
    Mirror object which contains mirror-level systems and commands. Such as GetProxyTemperature, GetConnectedStatus, etc

    Parameters
    ----------
    board
        Handle for the Board object

    Raises
    ------
    none

    Notes
    -----
    MRE2Mirror is a subclass of ProxyBoard. Refer to optoKummenberg.connections for methods, parameters, etc.

    Examples
    --------
    Instantiate a simple-mode Board with connection over COM12 port, with baud rate 9600. Then switch into pro-mode.
    This will not flush the firmware registers, so it is assumed to already be reset.

    >>> import optoMDC
    >>> mre2 = optoMDC.connect()
    >>> mre2.Mirror.GetConnectedStatus()

    """
    def __init__(self, board):
        _ProxyBoard.__init__(self, board)
        self.EEPROM = Registers.DeviceEEPROM(board)

        # channel-level systems
        self.Channel_0 = MRE2Channel(board, 0)
        self.Channel_1 = MRE2Channel(board, 1)

        # proxy board systems
        self.OpticalFeedback = Registers.OpticalFeedback(board)


class MRE2Channel(_Channel):
    r"""
    Channel object which contains channel-level systems and commands. Such as StaticInput, SetControlMode, etc

    Parameters
    ----------
    board
        Handle for the Board object
    channel_number
        integer of the channel (0 or 1 by default)

    Raises
    ------
    none

    Notes
    -----
    MRE2Channel is an subclass of Channel. Refer to optoKummenberg.connections for methods, parameters, etc.

    Examples
    --------
    Instantiate a simple-mode Board with connection over COM12 port, with baud rate 9600. Then switch into pro-mode.
    This will not flush the firmware registers, so it is assumed to already be reset.

    >>> import optoMDC
    >>> mre2 = optoMDC.connect()
    >>> mre2.Mirror.Channel_0.GetControlMode()
    >>> mre2.Mirror.Channel_1.SignalGenerator.GetAmplitude()

    """
    def __init__(self, board, channel_number: int = 0):
        _Channel.__init__(self, board, channel_number)

        # meta systems
        self.VectorPatternUnit = Registers.VectorPatternUnit(self._channel, self._board)
        self.VectorPatternUnit.Memory = self._board.VectorPatternMemory
        # inputs
        self.Analog            = Registers.Analog(self._channel, self._board)
        self.SignalGenerator   = Registers.SignalGenerator(self._channel, self._board)

        # control modes
        self.OFPID             = Registers.OFPID(self._channel, self._board)
        self.XYPID             = Registers.XYPID(self._channel, self._board)
