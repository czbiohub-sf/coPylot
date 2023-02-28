import numpy as np
import time
import struct
import inspect
from .tools.parsing_tools import encode, encode_vector
from .tools.command_tools import issue_command, process_simple_response, process_response, get_cmd_reg_val
from .tools.systems_registers_tools import process_registers
from .tools.definitions import (CMD_DELAY, ENDIAN, Units, Waveforms,
                                CommandID, SimpleResponses, ESCAPE_BYTE,
                                FRAME_BOUNDARY, ESCAPE_MASK)


# Kummenberg Commands
class Command:
    r"""
    Command object from which to send Board commands and process responses.
    Note: these commands are inherited by a given board (Duck typed)

    For Board information, see help(connection.Board) or connection.Board.__doc__

    Parameters
    ----------
    board : Board
        The Board object from which to issue commands and receive responses.

    Returns
    -------
    response : str
        Firmware response string, or parse_error code string.

    Raises
    ------
    none

    Notes
    -----
    Board commands operate via duck typing. Must pass a valid Board.
    Command success may depend on _board mode (simple/pro)

    Examples
    --------
    Given an existing _board connection (bd) in simple mode, this will perform a simple handshake acknowledgement.

    >>> Command(bd).handshake()
    Handshake Successful.

    """

    def __init__(self, board=None):
        pass

    # Simple Mode Commands
    def handshake(self, force: bool = False):
        r"""
        Acknowledge communication in simple mode.

        Parameters
        ----------
        force : bool
            Will first ensure board is in correct mode before sending command.

        Returns
        -------
        response : bytes
            Firmware response string, or parse_error code string.
        """
        if force:
            if self.verbose:
                print('Forcing Board into Simple Mode: May return Errors.')
            self._simple = self.IsSimpleMode()
            self._set_internal_mode(self._simple, simple_mode_desired=True)
            self.go_simple()

        if self._simple:
            response = issue_command(self, 'Start\r\n'.encode())
            if response in SimpleResponses.values():
                response = SimpleResponses['PROCESSED_WITHOUT_ERROR']
        else:
            response = 0xffff
        process_simple_response(self, inspect.stack()[0][3].upper(), response)
        return response

    def go_pro(self, force: bool = False):
        r"""
        Switches _board into pro-mode.

        Parameters
        ----------
        force : bool
            Will first ensure board is in correct mode before sending command.

        Returns
        -------
        response : bytes
            Firmware response string, or parse_error code string.
        """
        if force:
            if self.verbose:
                print('Forcing Board into Pro Mode: May return Errors.')
            self._simple = self.IsSimpleMode()
            self._set_internal_mode(self._simple, simple_mode_desired=True)

        response = issue_command(self, 'GoPro\r\n'.encode())
        if response is SimpleResponses['UNRECOGNIZED_MESSAGE']:
            response = self.go_pro()
        if response in SimpleResponses.values() and response is not SimpleResponses['UNRECOGNIZED_MESSAGE']:
            self._simple = False
        return response

    def reset(self, force: bool = False):
        r"""
        Reset firmware and reconnect to Board. Will be in simple-mode after reset.
        Must be in Simple Mode to execute this Command!

        Parameters
        ----------
        force : bool
            Will first ensure board is in correct mode before sending command.

        Returns
        -------
        response : bytes
            Firmware response string, or parse_error code string.
        """
        if force:
            if self.verbose:
                print('Forcing Board into Simple Mode: May return Errors.')
            self._simple = self.IsSimpleMode()
            self._set_internal_mode(self._simple, simple_mode_desired=True)

        if not self._simple:
            response = 0xffff
            return response

        self.Connection._comm_lock = False
        self.Connection.send('Reset\r\n'.encode())
        self.Connection.disconnect()
        time.sleep(1.5)
        self.Connection.connect()
        self.Connection._comm_lock = True

        if self.verbose:
            print('Verifying Simple via Handshake...')
        response = self.handshake()
        if response in SimpleResponses.values():
            self._simple = True

        return response

    # Pro Mode Commands
    def generic_command(self, force: bool = False):
        r"""
        Sends generic pro-mode command.

        Parameters
        ----------
        force : bool
            Will first ensure board is in correct mode before sending command.

        Returns
        -------
        response : bytes
            Firmware response string, or parse_error code string.
        """
        cmd_id = CommandID.GENERIC_COMMAND
        register = {'id': 0, 'type': int, 'unit': None, 'range': [0, 1]}
        value = 0

        if force:
            if self.verbose:
                print('Forcing Board into Pro Mode: May return Errors.')
            self._simple = self.IsSimpleMode()
            self._set_internal_mode(self._simple, simple_mode_desired=False)

        if self._simple:
            response = 0xffff
            return process_simple_response(self, inspect.stack()[0][3].upper(), response)
        else:
            data = encode(cmd_id, value)
            response = issue_command(self, data)
            parsed_response = process_response(cmd_id, register, value, response, self.verbose)
        if parsed_response[4]:
            # error flag was true
            print('Last Message Sent : {}'.format(self.Connection.last_sent))
        return parsed_response[2]

    def get_firmware_id(self, force: bool = False):
        r"""
        Gets firmware identification.

        Parameters
        ----------
        force : bool
            Will first ensure board is in correct mode before sending command.

        Returns
        -------
        response : bytes
            Firmware response string, or parse_error code string.
        """
        cmd_id = CommandID.GET_FIRMWARE_ID
        register = {'id': 0, 'type': int, 'unit': None, 'range': [0, 1]}
        value = 0

        if force:
            if self.verbose:
                print('Forcing Board into Pro Mode: May return Errors.')
            self._simple = self.IsSimpleMode()
            self._set_internal_mode(self._simple, simple_mode_desired=False)

        if self._simple:
            response = 0xffff
            return process_simple_response(self, inspect.stack()[0][3].upper(), response)
        else:
            data = encode(cmd_id, value)
            response = issue_command(self, data)
            parsed_response = process_response(cmd_id, register, value, response, self.verbose)
        if parsed_response[4]:
            # error flag was true
            print('Last Message Sent : {}'.format(self.Connection.last_sent))
        return parsed_response[2]

    def get_status(self, force: bool = False):
        r"""
        Gets the board status information.

        Parameters
        ----------
        force : bool
            Will first ensure board is in correct mode before sending command.

        Returns
        -------
        response : bytes
            Firmware response string, or parse_error code string.
        """
        cmd_id = CommandID.GET_STATUS
        register = {'id': 0, 'type': int, 'unit': None, 'range': [0, 1]}
        value = 0

        if force:
            if self.verbose:
                print('Forcing Board into Pro Mode: May return Errors.')
            self._simple = self.IsSimpleMode()
            self._set_internal_mode(self._simple, simple_mode_desired=False)

        if self._simple:
            response = 0xffff
            return process_simple_response(self, inspect.stack()[0][3].upper(), response)
        else:
            data = encode(cmd_id, value)
            response = issue_command(self, data)
            parsed_response = process_response(cmd_id, register, value, response, self.verbose)
        if parsed_response[4]:
            # error flag was true
            print('Last Message Sent : {}'.format(self.Connection.last_sent))
        return parsed_response[2]

    def start_self_test(self, force: bool = False):
        r"""
        Begins board self-test.

        Parameters
        ----------
        force : bool
            Will first ensure board is in correct mode before sending command.

        Returns
        -------
        response : bytes
            Firmware response string, or parse_error code string.
        """
        cmd_id = CommandID.START_SELF_TEST
        register = {'id': 0, 'type': int, 'unit': None, 'range': [0, 1]}
        value = 0

        if force:
            if self.verbose:
                print('Forcing Board into Pro Mode: May return Errors.')
            self._simple = self.IsSimpleMode()
            self._set_internal_mode(self._simple, simple_mode_desired=False)

        if self._simple:
            response = 0xffff
            return process_simple_response(self, inspect.stack()[0][3].upper(), response)
        else:
            data = encode(cmd_id, value)
            response = issue_command(self, data)
            parsed_response = process_response(cmd_id, register, value, response, self.verbose)
        if parsed_response[4]:
            # error flag was true
            print('Last Message Sent : {}'.format(self.Connection.last_sent))
        return parsed_response[2]

    def load_snapshot(self, memory_id: int, force: bool = False):
        r"""
        Loads snapshot at given memory location, may not work if id is invalid.
        For more information, see: SnapshotManager in registers.

        Parameters
        ----------
        memory_id : int
            Memory location to load.
        force : bool
            Will first ensure board is in correct mode before sending command.

        Returns
        -------
        response : bytes
            Firmware response string, or parse_error code string.
        """
        cmd_id = CommandID.LOAD_CONFIG
        register = {'id': 0, 'type': int, 'unit': None, 'range': [0, 7]}
        value = memory_id

        if force:
            if self.verbose:
                print('Forcing Board into Pro Mode: May return Errors.')
            self._simple = self.IsSimpleMode()
            self._set_internal_mode(self._simple, simple_mode_desired=False)

        data = encode(cmd_id, value)
        response = issue_command(self, data)

        parsed_response = process_response(cmd_id, register, value, response, self.verbose)
        if parsed_response[4]:
            # error flag was true
            print('Last Message Sent : {}'.format(self.Connection.last_sent))
        return parsed_response[2]

    def save_snapshot(self, memory_id: int, force: bool = False):
        r"""
        Saves snapshot at given memory location, may not work if id is invalid. (i.e. location 0 is readonly)
        For more information, see: SnapshotManager in registers.

        Parameters
        ----------
        memory_id : int
            Memory location to save.
        force : bool
            Will first ensure board is in correct mode before sending command.

        Returns
        -------
        response : bytes
            Firmware response string, or parse_error code string.
        """
        cmd_id = CommandID.STORE_CONFIG
        register = {'id': 0, 'type': int, 'unit': None, 'range': [0, 7]}
        value = memory_id

        if force:
            if self.verbose:
                print('Forcing Board into Pro Mode: May return Errors.')
            self._simple = self.IsSimpleMode()
            self._set_internal_mode(self._simple, simple_mode_desired=False)

        data = encode(cmd_id, value)
        response = issue_command(self, data, cmd_delay=1)
        parsed_response = process_response(cmd_id, register, value, response, self.verbose)
        if parsed_response[4]:
            # error flag was true
            print('Last Message Sent : {}'.format(self.Connection.last_sent))
        return parsed_response[2]

    def go_simple(self, force: bool = False):
        r"""
        Switches _board into simple-mode.

        Parameters
        ----------
        force : bool
            Will first ensure board is in correct mode before sending command.

        Returns
        -------
        response : bytes
            Firmware response string, or parse_error code string.
        """
        cmd_id = CommandID.SET_COMM_MODE
        register = {'id': 0, 'type': int, 'unit': None, 'range': [0, 1]}
        value = 0
        data = encode(CommandID.SET_COMM_MODE, 0)

        if force:
            if self.verbose:
                print('Forcing Board into Pro Mode: May return Errors.')
            self._simple = self.IsSimpleMode()
            self._set_internal_mode(self._simple, simple_mode_desired=False)

        if self._simple:
            response = 0xffff
            return process_simple_response(self, 'Go Simple', response)
        else:
            response = issue_command(self, data)
            parsed_response = process_response(cmd_id, register, value,
                                               response, self.verbose) if not self.simulated else (None,)*5

        if parsed_response[1] == CommandID.SET_COMM_MODE or force or self.simulated:
            self._simple = True
            if self.verbose:
                print('Verifying Simple via Handshake...')
            simple_mode_check = self.handshake()
            if not simple_mode_check in SimpleResponses.values():
                # Try again once
                simple_mode_check = self.handshake()
                if not simple_mode_check in SimpleResponses.values():
                    self._simple = False

        # return slave_id, response_id, response_data, crc
        return response

    def set_value(self, register: dict or list or int, value, cmd_delay: float = None):
        r"""
        Sets the given registers to desired value.

        Parameters
        ----------
        register : dict or list of dicts or int or list of ints
            Register dictionary corresponding to desired registers.{'id': registers number, 'type': data type, ...}
            Further, a raw registers id can be passed, in which case no validation will occur (COULD CAUSE ERRORS).
        value : varies, can also be list of values
            The type and range of value is dependent on the registers being addressed, see 'type' element above.
        cmd_delay : float
            Amount of additional time in seconds to wait between send / receive.

        Returns
        -------
        str
            Firmware response, contains acknowledgement or parse_error information.

        Raises
        ------
        none

        See Also
        --------
        Register IDs, value type and range can be found in the registers module.

        Examples
        --------
        In this example, the same _board (con) is used and the X channel OF is set to 0 over USB/UART
        Note: system and registers name must be known, see registers module for more info.

        >>> from registers.generic_registers import StaticInput
        >>> from src.main.python.optoKummenberg.connections import Board
        >>> board = Board()
        >>> registers = StaticInput(0).of
        >>> board.set_value(registers, 0.0)

        """
        # get hex information from registers & values
        cmd_reg_val = get_cmd_reg_val(command=CommandID.SET_VALUE, register=register, value=value)
        if cmd_reg_val == (None, None, None):
            return [None]
        else:
            # perform encode, issue, process
            data = encode(*cmd_reg_val)
            response = issue_command(self, data, cmd_delay=cmd_delay)
            parsed_response = process_response(cmd_reg_val[0], register, value, response, self.verbose)

            if parsed_response[4]:
                # error flag was true
                print('Last Message Sent : {}'.format(self.Connection.last_sent))
            return parsed_response[2]

    def get_value(self, register: dict or list):
        r"""
        Gets the given registers value.

        Parameters
        ----------
        register_record : dict or list
            Register dictionary fields corresponding to register.{'id': registers number, 'type': data type, ...}
        set_internal : bool
            Determines whether to set the returned value internally. (recommended)

        Returns
        -------
        str
            Firmware response, contains registers value, along with acknowledgement or parse_error information.

        Raises
        ------
        none

        See Also
        --------
        Register IDs, value type and range can be found in the registers module.

        Examples
        --------
        In this example, the same _board (_board) is used and the X channel OF is set to 0.0 over USB/UART
        Note: system and registers name must be known, see registers module for more info.

        >>> board.initialize_channel(0)
        >>> register_record = board.Channel_0.StaticInput.of
        >>> board.get_value(register_record)
        Sending: b'~\x00\x11\x02P\x01\x00\x00~'
        Received: b'~\x00\x11\x04\x00\x00\x00\x00\xf2\x81~'
        Command: [GET_VALUE]. Register: [0x5001]. Value: [[0.0]].
        Data Received: [0.0]
        (0, 17, [0.0], [242, 129])

        """
        # get hex information from registers & values
        cmd_reg_val = get_cmd_reg_val(command=CommandID.GET_VALUE, register=register, value=None)

        # synthetic value used for simulated connection
        value = None
        if self.Connection._port is None:
            if isinstance(register, list):
                value = [item['value'] for item in register]
            elif isinstance(register, dict):
                value = register['value']
        if cmd_reg_val == (None, None, None):
            return [None]
        else:
            # perform encode, issue, process
            data = encode(*cmd_reg_val)
            response = issue_command(self, data)
            parsed_response = process_response(cmd_reg_val[0], register, value, response, self.verbose)
            if parsed_response[4]:
                # error flag was true
                print('Last Message Sent : {}'.format(self.Connection.last_sent))
            return parsed_response[2]

    def set_vector(self, register: dict or int, index: int, vector, cmd_delay=None):
        r"""
        Sets the given register vector to desired value.

        Parameters
        ----------
        register : dict or list of dicts or int or list of ints
            Register dictionary corresponding to desired registers.{'id': registers number, 'type': data type, ...}
            Further, a raw registers id can be passed, in which case no validation will occur (COULD CAUSE ERRORS).
        index : int
            The location to store the given vector.
        value : varies, can also be list of values
            The type and range of value is dependent on the registers being addressed, see 'type' element above.
        cmd_delay : float
            How long to wait for response in secs. By default is set to registers.CMD_DELAY


        Returns
        -------
        str
            Firmware response, contains acknowledgement or parse_error information.

        Raises
        ------
        none

        See Also
        --------
        Register IDs, value type and range can be found in the registers module.

        Examples
        --------
        In this example, the same _board (con) is used and the X channel OF is set to 0 over USB/UART
        Note: system and registers name must be known, see registers module for more info.

        >>> from registers.generic_registers import VectorPatternMemory
        >>> from src.main.python.optoKummenberg.connections import Board
        >>> board = Board()
        >>> register = {'id': VectorPatternMemory().sys_id << 8, 'type': float}  # could also send register = 0x2600
        >>> vector = [0, 0.1, 0.2, 0.3]
        >>> board.set_vector(register, 0, vector)

        """
        if cmd_delay is None:
            cmd_delay = CMD_DELAY

        # perform encode, issue, process
        byte_string = encode_vector(register=register, index=index, vector=vector)
        response = issue_command(self, byte_string, cmd_delay=cmd_delay)
        parsed_response = process_response(command_id_sent=CommandID.SET_VECTOR,
                                           register=register, value=vector, response=response,
                                           verbose=self.verbose)
        if parsed_response[4]:
            # error flag was true
            print('Last Message Sent : {}'.format(self.Connection.last_sent))
        return parsed_response[2]

    def get_vector(self, register: dict or int, index: int, count: int):
        r"""
        Gets the given register vector.

        Parameters
        ----------
        register : int
            The system location of the desired vector.
        index : int
            The location of the vector to begin reading from.
        count :
            The number of vector elements, where each elements is 4 bytes if float/int or 1 byte otherwise.

        Returns
        -------
        str
            Firmware response, contains registers value, along with acknowledgement or parse_error information.

        Raises
        ------
        none

        See Also
        --------
        Register IDs, value type and range can be found in the registers module.

        Examples
        --------
        In this example, the same _board (_board) is used and the X channel OF is set to 0.0 over USB/UART
        Note: system and registers name must be known, see registers module for more info.

        >>> board.initialize_channel(0)
        >>> register_record = board.Channel_0.StaticInput.of
        >>> board.get_value(register_record)
        Sending: b'~\x00\x11\x02P\x01\x00\x00~'
        Received: b'~\x00\x11\x04\x00\x00\x00\x00\xf2\x81~'
        Command: [GET_VALUE]. Register: [0x5001]. Value: [[0.0]].
        Data Received: [0.0]
        (0, 17, [0.0], [242, 129])

        """
        index, count = index*4, count*4
        cmd_id = CommandID.GET_VECTOR
        if type(register) is int:
            register_id = register
        else:
            register_id = register['id']
            if register['type'] is not float:
                index, count = index//4, count//4

        # encode, issue, process
        byte_string = encode(command_id=CommandID.GET_VECTOR, register_id=register_id, data=[index, count])
        response = issue_command(board=self, command_bytes=byte_string, cmd_delay=CMD_DELAY)
        # parsed_response = process_response(cmd_id, register, count, response, self.verbose)
        parsed_response = process_response(command_id_sent=cmd_id,
                                           register=register, value=None, response=response,
                                           verbose=self.verbose)
        if parsed_response[4]:
            # error flag was true
            print('Last Message Sent : {}'.format(self.Connection.last_sent))
        return parsed_response[2]

    def disconnect(self):
        r"""
        Severs the serial connection, flushing input/output buffers.
        """
        self.Connection.disconnect()
