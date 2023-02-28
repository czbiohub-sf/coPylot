import serial
from .registers import generic_registers as registers
from .tools.definitions import UnitType, CommandID, FRAME_BOUNDARY, SimpleResponses, CMD_DELAY
from .commands import Command
from .tools.command_tools import issue_command
import time
from warnings import warn
from sys import exit


class Connection:
    r"""
    Connection object from which to connect/disconnect and send/receive data.

    For Serial Communication, See Also: PySerial API Documentation
        https://pyserial.readthedocs.io/en/latest/pyserial_api.html
    or use help(serial).

    Parameters
    ----------
    port : str or None
        The port is immediately opened on object creation, when a port is given.
        It is not opened when port is None and a successive call to open() is required.
        port is a device name: depending on operating system. e.g. /dev/ttyUSB0 on GNU/Linux or COM3 on Windows.
    baudrate : int
        The parameter baudrate can be one of the standard values:
        50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200.
        These are well supported on all platforms.
        Standard values above 115200, such as:
        230400, 460800, 500000, 576000, 921600, 1000000, 1152000, 1500000, 2000000, 2500000, 3000000, 3500000, 4000000
        also work on many platforms and devices.
    comm_lock : bool = True
        Communication is disabled if this parameter is True, which is default. This prevents sending and receiving over
        the channel.
    timeout : float
        timeout = None: wait forever / until requested number of bytes are received
        timeout = 0: non-blocking mode, return immediately in any case, returning zero or more,
            up to the requested number of bytes
        timeout = x: set timeout to x seconds (float allowed) returns immediately when the requested
            number of bytes are available, otherwise wait until the timeout expires and return all
            bytes that were received until then.
    verbose : bool
        Verbose serial output for debugging/etc. If true, output generated even without parse_error/failures.

    Raises
    ------
    SerialException
        Unable to establish connection over given port.

    Notes
    -----
    To prevent communication issues, make sure that the comm_lock is False for only one device at a time.

    Examples
    --------
    Instantiate a connection on COM3, with baud rate 9600

    >>> con = Connection('COM3', 9600, verbose=True)
    Establishing Connection via port [COM3]...
    Connected.

    """

    def __init__(self, port: str or None, baudrate: int, inter_byte_timeout: float,
                 comm_lock: bool, timeout: float, verbose: bool):
        self._port               = port
        self._baudrate           = baudrate
        self._inter_byte_timeout = inter_byte_timeout
        self._comm_lock          = comm_lock
        self._timeout            = timeout
        self._serial_conn        = None
        self._settings           = None
        self.verbose             = verbose
        self.last_sent           = None

        if port is not None:
            # make connection to input
            self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    @staticmethod
    def _read(serial_connection, length: int = None, terminator: bytes = None):
        if terminator is None:
            if length is None:
                return serial_connection.read(serial_connection.inWaiting())
            else:
                return serial_connection.read(size=length)
        else:
            return serial_connection.read_until(terminator)

    def send(self, data: bytes):
        r"""
        Send bytes array over connection.

        Parameters
        ----------
        data : bytes
            Bytes object to send.

        Returns
        -------
        none

        Raises
        ------
        none

        Notes
        -----
        Bytes must be properly encoded, see example.

        Examples
        --------
        First line: Set _board to pro mode.
        Second Line: Set value (0x10) of USB/UART (0x50) OF (0x00) registers to 0.
        Third Line: Same as above, without using encoder.

        >>> con = Connection('COM12', 9600, verbose=True)
        Establishing Connection via port [COM3]...
        Connected.
        >>> con._comm_lock = False
        >>> con.send('gopro\r\n'.encode())
        DEBUG: Sending 'b'gopro\r\n''
        >>> con.send(con.encode(0x10,0x5000,0))
        DEBUG: Sending 'b'~\x00\x10\x06P\x00\x00\x00\x00\x00\x00\x00~''
        >>> con.send(b'~\x00\x10\x06P\x00\x00\x00\x00\x00\x00\x00~')
        DEBUG: Sending 'b'~\x00\x10\x06P\x00\x00\x00\x00\x00\x00\x00~''

        """
        if self._port is not None:
            try:
                self._serial_conn.write(data)
                if self.verbose:
                    if data[-1] == 0x0a:
                        print('Sending: {}'.format(data))
                    else:
                        print('Sending: {}'.format(data.hex()))
            except AttributeError:
                print('WRITE ERROR: No Connection')
        elif self.verbose:
            print('DEBUG: Sending \'{}\''.format(data))
        self.last_sent = data

    def receive(self, length: int = None, terminator: bytes = None):
        r"""
        Receive bytes array over connection.

        Parameters
        ----------
        length : int, optional
            Return given number of bytes.
        terminator : bytes, optional
            The communication will proceed until the terminator is received.
            The remaining data will still exist in the firmware buffer.

        Returns
        -------
        bytes array
            Encoded byte array returned.

        Raises
        ------
        none

        Examples
        --------
        Assuming the 'gopro' command was just sent, a response will be transmitted by the MRE2 firmware.

        >>> con.receive()
        Received: b'OK\r\n'

        """
        if self._port is not None:
            data = self._read(self._serial_conn, length, terminator)
            if terminator == bytes([FRAME_BOUNDARY]):
                data += self._read(self._serial_conn, length, terminator)
                while data == terminator:
                    data += self._read(self._serial_conn, length, terminator)
            if self.verbose:
                if 0x0a in data:
                    if data[-1] == 0x0a:
                        print('Received: {}'.format(data))
                    else:
                        print('Received: {}'.format(data.hex()))
                else:
                    print('Received: {}'.format(data.hex()))

        else:
            data = b'OK\r\n'
            if self.verbose:
                print('DEBUG: Received Simulated Response {}'.format(data))

        return data

    def connect(self):
        r"""
        Establish serial connection over port. Will reattempt up to 3 times.

        Parameters
        ----------
        none

        Returns
        -------
        none

        Raises
        ------
        SerialException
        """
        if self.verbose:
            print('Establishing Connection via port [{}]...'.format(self._port))
        if self._port is not None:
            attempts = 0
            while attempts < 3:
                try:
                    # connect
                    attempts += 1
                    self._serial_conn = serial.Serial(port=self._port, baudrate=self._baudrate, timeout=self._timeout,
                                                      interCharTimeout=self._inter_byte_timeout)
                    self._settings = self._serial_conn.getSettingsDict()
                    if self.verbose:
                        print('Connected.')
                    break
                except serial.serialutil.SerialException:
                    err_args = serial.serialutil.SerialException.args
                    if hasattr(self, '_serial_conn'):
                        del self._serial_conn
                    print('Unable to Connect.')
                    print('Retrying Connection...')
                    pass
            if attempts == 3:
                print('Exiting.')
                exit()
        elif self.verbose:
            print('DEBUG MODE: Connection Simulated.')

    def disconnect(self):
        r"""
        Terminates the connection with a given _board.

        Returns
        -------
        none

        Raises
        ------
        none

        Examples
        --------
        >>> con.disconnect()
        Flushing input-output buffers...
        Closing Connection...
        Disconnected.

        """
        if self._port is not None:
            if self.verbose:
                print('Flushing input-output buffers...')
            self._serial_conn.flush()
            if self.verbose:
                print('Closing Connection...')
            self._serial_conn.close()
        if self.verbose:
            print('Disconnected.')


class Board(Command):
    r"""
    Board object from which to issue MRE2 commands over connection.

    Parameters
    ----------
    port, baudrate, comm_lock, timeout, verbose
        Extended from Connection class
    simple: bool, optional
        Determines whether or not Board will be set in simple-mode after initialization.
    board_reset: bool, optional
        Determines whether or not to reset the Board during initialization.
    number_of_channels: int
        How many channel will be instantiated during initalization.

    Raises
    ------
    none

    Notes
    -----
    Board extends Connection class. Refer to Connection for parameters, etc.

    Examples
    --------
    Instantiate a simple-mode Board with connection over COM12 port, with baud rate 9600. Then switch into pro-mode.
    This will not flush the firmware registers, so it is assumed to already be reset.

    >>> board = Board(port='COM12', baudrate=9600, verbose=True, simple=True)
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
    def __init__(self, port: str or None = None, baudrate: int = 115200, comm_lock: bool = True,
                 timeout: float = None, verbose: bool = False, simple: bool = False,
                 board_reset: bool = False, inter_byte_timeout: float = 0.2):
        self.verbose = verbose
        self.simulated = port is None
        if self.simulated:
            warn("This is a simulated connection: Serial Port = None. "
                 "If this is unintended, try explicitly stating the port", RuntimeWarning)
        # default board-level systems
        self.Status = registers.Status(board=self)
        self.EEPROM = registers.BoardEEPROM(board=self)
        self.SnapshotManager = registers.SnapshotManager(board=self)

        # default proxy board
        self.ProxyBoard = ProxyBoard(board=self)

        # default channels
        self.channel = [self.ProxyBoard.Channel_0]

        # default connection and Kummenberg commands
        self.Connection = Connection(port, baudrate, inter_byte_timeout, comm_lock, timeout, verbose)
        self.Commands = Command()
        Command.__init__(self)
        self._simple = self.IsSimpleMode()
        self._set_internal_mode(self._simple, simple)

    def ResetChannel(self, channel_to_reset: int):
        r"""
        Reset given channel to static input in open-loop mode, with input value 0. Reset Gain/Offset.

        Returns
        -------
        none

        Raises
        ------
        none

        Examples
        --------
        >>> board.reset_channel(0)
        Flushing input-output buffers...
        Closing Connection...
        Disconnected.

        """
        if len(self.channel) > channel_to_reset:
            if self.verbose:
                print('Resetting Channel {} to Static Input with 0 Amps...'.format(channel_to_reset))
            self.channel[channel_to_reset].SetControlMode(UnitType.CURRENT)
            self.channel[channel_to_reset].StaticInput.SetCurrent(0.0)
            self.channel[channel_to_reset].StaticInput.SetAsInput()
            self.channel[channel_to_reset].InputConditioning.SetGain(1.0)
            self.channel[channel_to_reset].InputConditioning.SetOffset(0.0)
            if self.verbose:
                print('Channel {} Reset to Default State.'.format(channel_to_reset))
        else:
            print('Channel {} is not a Valid Channel Number.'.format(channel_to_reset))

    def IsSimpleMode(self):
        r"""
        Will determine if board is in simple-mode.

        Returns
        -------
        is_simple_mode: bool

        Raises
        ------
        none

        Examples
        --------
        >>> board.IsSimpleMode()

        """
        self.Connection._comm_lock = False
        started_correctly = False
        num_attempts = 0
        ack = b''

        while not started_correctly and num_attempts < 3:
            self.Connection.send(b'Start\r\n')
            time.sleep(CMD_DELAY)
            ack = self.Connection.receive()
            if ack != b'':
                started_correctly = True
            else:
                num_attempts += 1
                time.sleep(CMD_DELAY)

        if ack in SimpleResponses.values():
            is_simple_mode = True
        # we enter here if we received pro garbage OR
        # if we havent received anz response in the 3 Start attempts
        else:
            status_cmd = bytes([FRAME_BOUNDARY, 0, CommandID.GET_STATUS, 2, 0, 0, 0, 0, FRAME_BOUNDARY])
            issue_command(self, status_cmd)
            is_simple_mode = False
        self.Connection._comm_lock = True
        return is_simple_mode

    def _set_internal_mode(self, current_mode_is_simple, simple_mode_desired):
        if simple_mode_desired:
            if current_mode_is_simple:
                self._simple = True
            elif not current_mode_is_simple:
                if self.verbose:
                    print('Initializing Board in Simple Mode...')
                self.go_simple()
                if self.verbose:
                    print('Board Initialized in Simple Mode.')
        elif not simple_mode_desired:
            if current_mode_is_simple:
                if self.verbose:
                    print('Initializing Board in Pro Mode...')
                self.go_pro()
                if self.verbose:
                    print('Board Initialized in Pro Mode.')
            elif not current_mode_is_simple:
                self._simple = False
        return


class ProxyBoard:
    r"""
    Generic Proxy Board object with a single channel.

    Parameters
    ----------
    board
        connections.Board object

    Raises
    ------
    none

    Notes
    -----
    Board extends Connection class. Refer to Connection for parameters, etc.

    """
    def __init__(self, board):
        self._board = board
        self.Channel_0 = Channel(board)

    def GetConnectedStatus(self):
        r"""
        Determines whether proxy board is connected and responding.

        Parameters
        ----------
        none

        Raises
        ------
        none

        Returns
        -----
        bool

        """
        return not self._board.Status.GetErrorFlagRegister()


class Channel:
    r"""
    Generic Channel object with default systems and commands. Such as StaticInput, SetControlMode, etc

    Parameters
    ----------
    board
        connections.Board object
    channel: int
        channel identifier, required for system and register identification

    Raises
    ------
    none
    """
    def __init__(self, board, channel_number: int = 0):
        self._board = board
        self._channel = channel_number
        self._control_mode = UnitType.CURRENT

        # default meta systems
        self.Manager           = registers.Manager(self._channel, self._board)

        # default stages
        self.StaticInput       = registers.StaticInput(self._channel, self._board)
        self.InputConditioning = registers.InputConditioning(self._channel, self._board)
        self.FeedThrough       = registers.CurrentFeedThrough(self._channel, self._board)
        self.LinearOutput      = registers.LinearOutput(self._channel, self._board)

    def GetControlMode(self):
        r"""
        Retrieves board control mode for this channel.

        Parameters
        ----------
        none

        Raises
        ------
        none

        Returns
        -----
        UnitType
            Control mode options set by register_tables.UnitType

        """
        response = self.Manager.get_register('control')

        if response[0] == 0xB0 | self._channel:  # Feed Through Control Mode
            self._control_mode = UnitType.CURRENT
            return self._control_mode

        if response[0] == 0xB8 | self._channel:  # OF PID Control Mode
            self._control_mode = UnitType.OF
            return self._control_mode

        if response[0] == 0xC0 | self._channel:  # XY PID Control Mode
            self._control_mode = UnitType.XY
            return self._control_mode

    def SetControlMode(self, control_mode: UnitType or str):
        r"""
        Sets board control mode for this channel.

        Parameters
        ----------
        control_mode: UnitType or str
            Mode to set must be in register_tables.UnitType or appropriate string format given by
            UnitType enum attribute names.

        Raises
        ------
        none

        Returns
        -----
        str
            Firmware response or error information

        """
        if type(control_mode) is str:
            control_mode = UnitType.__members__[control_mode.upper()]

        if control_mode == UnitType.CURRENT and hasattr(self, 'FeedThrough'):
            response = self.FeedThrough.SetAsControlMode()
        elif control_mode == UnitType.OF and hasattr(self, 'OFPID'):
            response = self.OFPID.SetAsControlMode()
        elif control_mode == UnitType.XY and hasattr(self, 'XYPID'):
            response = self.XYPID.SetAsControlMode()
        else:
            return False

        self._control_mode = control_mode
        return response

    def initialize_channel(self):
        self.__init__(self._board, self._channel)

    # def _synchronize_channel(self):
    #     """
    #     Currently Unused. Intended for resetting register['value'], such that state could be stored in a log file and
    #     system returned to restore point.
    #     :return:
    #     """
    #     if self._board.verbose:
    #         print('Channel {} Synchronizing with firmware...'.format(self._channel))
    #     channel_systems = [system[1] for system in inspect.getmembers(self) if
    #                        type(system[1]) in systems()]
    #
    #     for i in range(len(channel_systems)):
    #         register_names = [name for name in channel_systems[i].__dict__ if not name.startswith('_')]
    #         for j in range(len(register_names)):
    #             register_name = register_names[j]
    #             register = channel_systems[i].__dict__[register_name]
    #             value = self._board.get_value(register)[2]
    #             if self._board.verbose:
    #                 print('Internally, {} {} set to {}'
    #                       .format(channel_systems[i].__class__.__name__, register_name, value))
    #
    #     if self._board.verbose:
    #         print('Channel {} Synchronized with firmware.'.format(self._channel))


