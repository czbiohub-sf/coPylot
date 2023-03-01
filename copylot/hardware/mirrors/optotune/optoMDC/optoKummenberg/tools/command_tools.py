import struct
import time
import serial
from ..tools.parsing_tools import parse_error, encode, decode
from ..tools.definitions import (CMD_DELAY, ENDIAN, FRAME_BOUNDARY,
                                 SimpleResponses, commandID, commandName,
                                 WaveformShape, UnitType)
from ..tools.systems_registers_tools import process_registers
import numpy as np


def issue_command(board, command_bytes, cmd_delay: float = None):
    r"""
    Issues given command_bytes over _board connection. Will attempt 3 times.

    This method unlocks the comm_lock, sends the desired data, receives a response, then reapplies the lock.

    Parameters
    ----------
    board : Board
        The board to issue a command over.
    command_bytes : bytes or int or str
        The byte array to send over the connection.

    Returns
    -------
    str
        Firmware response, contains acknowledgement or parse_error information. In DEBUG mode this returns the internal state.

    Raises
    ------
    none

    See Also
    --------
    Command bytes must be properly encoded, see registers encode function.

    """
    board.Connection._comm_lock = False
    number_of_attempts = 0
    response = b''

    if cmd_delay is None:
        cmd_delay = CMD_DELAY

    while response == b'' and number_of_attempts < 3:
        try:
            # clear output buffer
            temp = board.Connection.verbose
            board.Connection.verbose = False
            junk = board.Connection.receive()
            board.Connection.verbose = temp
            if junk != b'':
                response = junk
                break
            if board.Connection.verbose and junk != b'':
                print('Output Buffer Cleared. [data={}]'.format(junk))

            # call and respond
            board.Connection.send(command_bytes)
            time.sleep(cmd_delay)
            if not hasattr(board, '_simple'):
                reponse = board.Connection.receive()
            else:
                if board._simple:
                    response = board.Connection.receive(terminator='\n')
                elif not board._simple:
                    response = board.Connection.receive(terminator=bytes([FRAME_BOUNDARY]))
            board.Connection._serial_conn.flush()
            number_of_attempts += 1
            break

        # exception handling
        except serial.serialutil.SerialException:
            err_args = serial.serialutil.SerialException.args
            print('Unable to Communicate.')
            print('Retrying...')
            response = err_args
            print(err_args)
            number_of_attempts += 1
        except AttributeError:
            err_args = serial.serialutil.SerialException.args
            print('Serial Connection does not exist. Is the port ID valid?')
            print('Retrying...')
            response = err_args
            number_of_attempts += 1

    # Check connection after 3 failed attempts. Try to reconnect
    if number_of_attempts >= 3:
        attempt_reconnect(board)

    board.Connection._comm_lock = True

    return response


def attempt_reconnect(board):
    r"""
    Will attempt to reconnect to board. Will attempt 3 times.

    Parameters
    ----------
    board : Board
        The board to attempt reconnect.

    Returns
    -------
    none

    Raises
    ------
    Upon failure, will dump serial information.

    """
    try:
        print('Connection Failed. Resetting Connection and Synchronizing to Board...')
        board.disconnect()
        time.sleep(1)
        board.Connection._serial_conn.open()
    except:
        err_args = serial.serialutil.SerialException.args
        print('No Connection. Unable to Reconnect.')
        print('Argument Dump: {}'.format(err_args))
        print('Serial Connection: {}'.format(board.Connection._serial_conn))
        print('Serial Settings: {}'.format(board.Connection._settings))
        exit()


def process_simple_response(board, process_name: str, received_response: bytes):
    r"""
    Processes firmware simple response to determine if successful.

    Parameters
    ----------
    board : Board
        The object sending/receiving.
    process_name : str
        The name of the attempted process, for output statement.
    received_response : bytes
        The response received over the communication channel.

    Returns
    -------
    processed_response or error_response
        Decoded firmware response

    Raises
    ------
    none

    """
    if received_response == b'':
        return 'Empty Response...'

    if board._simple:
        if received_response == SimpleResponses['PROCESSED_WITHOUT_ERROR']:
            if board.verbose:
                print('{} Successful.'.format(process_name))
            processed_response = received_response
        elif received_response in SimpleResponses.values():
            if board.verbose:
                print('{} NOT Successful.'.format(process_name))
            processed_response = received_response
        else:
            err_args = parse_error(received_response)
            print('{} NOT Successful: {}.'.format(process_name, err_args))
            processed_response = err_args
    else:
        processed_response = parse_error(0xffff)
        print('{} NOT Successful: {}'.format(process_name, processed_response))

    return processed_response


def process_response(command_id_sent: int, register, value, response, verbose=False):
    r"""
    Processes firmware response.

    Parameters
    ----------
    command_id_sent : int
        The attempted command, see: commandID dictionary for potential values.
    register : dict or list of dicts or int or list of ints
        Register dictionary corresponding to desired registers.{'id': registers number, 'type': data type, ...}
    value
        The value or values that were originally destined to be transmitted.
    response : bytes or int or str
        Firmware response.
    verbose : bool = False
        Output verbosity.
    simulated : bool = False
        Whether connection over port is simulated, thus response is simulated.

    Returns
    -------
    slave_id, command_id, response_data, crc
        Decoded firmware response

    Raises
    ------
    none

    """
    if type(response) is not bytes or response == b'':
        return 0, 0, response, 0

    processed_response = decode(response)
    if processed_response is None:
        # comm parse_error
        print('ERROR: Communication Error.')
        return 0, 0, [0x0, 0xf, 0x0, 0xf], 0, True
    slave_id = processed_response[0]
    command_id  = processed_response[1]

    response_data = []
    if command_id == commandID['GET_VALUE']:
        # get single
        data_size = processed_response[2]
        raw_data = processed_response[3:data_size + 3]
        if type(register) is int:
            # return raw bytes, since only register id given
            response_data = raw_data
        elif register['type'] is int:
            response_data.append(struct.unpack(ENDIAN+'i', raw_data)[0])
        elif register['type'] is float:
            response_data.append(struct.unpack(ENDIAN+'f', raw_data)[0])
        elif register['type'] is bool:
            response_data.append(struct.unpack(ENDIAN+'i', raw_data)[0])

    if command_id == commandID['GET_MULTIPLE']:
        # get multiple
        data_size = processed_response[4]
        for i in range(data_size):
            start_byte = 1 + 4*(1+i)
            end_byte   = 5 + 4*(1+i)
            data_bytes = processed_response[start_byte:end_byte]
            if register[i]['type'] is int:
                data_bytes = struct.unpack(ENDIAN+'i', data_bytes)[0]
            elif register[i]['type'] is float:
                data_bytes = struct.unpack(ENDIAN+'f', data_bytes)[0]
            elif register[i]['type'] is bool:
                data_bytes = struct.unpack(ENDIAN+'i', data_bytes)[0]
            response_data.append(data_bytes)

    if command_id_sent == commandID['GET_VECTOR']:
        data_size = processed_response[2]
        if register['type'] in [str, bytes]:
            data_bytes = processed_response[3:data_size+3]
            response_data.append(data_bytes)
        elif data_size > 0:
            for i in range(data_size//4):
                start_byte = 3 + 4 * i
                end_byte = 7 + 4 * i
                data_bytes = processed_response[start_byte:end_byte]
                if register['type'] is int:
                    data_bytes = struct.unpack(ENDIAN + 'i', data_bytes)[0]
                elif register['type'] is float:
                    data_bytes = struct.unpack(ENDIAN + 'f', data_bytes)[0]
                response_data.append(data_bytes)

    if command_id_sent | 0x80 == command_id:
        # parse_error response!
        data_size = processed_response[2]
        response_data = processed_response[3:data_size + 3]
        # response_data = struct.unpack(ENDIAN+'i', response_data)

    response_data = list(response_data)
    crc = [processed_response[-2], processed_response[-1]]

    command_name = commandName[command_id_sent]
    err = True

    # success
    if command_id_sent == command_id:
        err = False
        if isinstance(register, list):
            register_id = [reg['id'] for reg in register]
            register_names = [hex(reg_id) for reg_id in register_id]
            if verbose:
                print('Command: [{}] Registers: [{}]. Values: [{}].'
                      .format(command_name, register_names, response_data))
        elif isinstance(register, dict):
            register_id = register['id']
            if verbose:
                print('Command: [{}]. Register: [{}]. Value: {}.'.format(command_name, hex(register_id), response_data))

    # not success
    elif command_id_sent != command_id:
        print('ERROR: Command ID Mismatch.')
        print('ID Expected: {}. ID Received: {}'.format(hex(command_id_sent), hex(command_id)))
        if command_id_sent | 0x80 == command_id:
            code = response_data[0] << 24 | \
                   response_data[1] << 16 | \
                   response_data[2] << 8 | \
                   response_data[3] << 0
            err_code = parse_error(code)
            print('This Corresponds to Error Code: {}>>{}'.format(code, err_code))
        else:
            print('This Corresponds to an Unknown Error Code.')
        print('Received Data Dump: {}'.format(response))

    return slave_id, command_id, response_data, crc, err


def get_cmd_reg_val(command, register: dict or list or int, value=None):
    r"""
    Given register(s) and value(s) will return command_id, register_id, value.

    Parameters
    ----------
    command : string or int related to command type 'SET_VALUE', 'GET_VALUE', etc with no determination of MULTIPLE
    register : dict or list of dicts or int or list of ints
        Register dictionary corresponding to desired registers.{'id': registers number, 'type': data type, ...}
        Further, a raw registers id can be passed, in which case no validation will occur (COULD CAUSE ERRORS).
    value : varies, can also be list of values
        The type and range of value is dependent on the registers being addressed, see 'type' element above.

    Returns
    -------
    cmd_id
        Hex value corresponding to proper command (1 Byte).
    reg_id
        Hex value corresponding to proper register (2 Bytes).
    value
        Validated value for the given register.

    Raises
    ------
    none

    See Also
    --------
    Register IDs, value type and range can be found in the registers module.

    Examples
    --------
    In this example, set value command for static input OF on channel 1 to 0.1 is expected.

    >>> from optoKummenberg.registers.generic_registers import StaticInput
    >>> res=get_cmd_register_value(0x10, 0x5100, 0.1)
    >>> print(encode(*res))
    b'~\x00\x10\x06Q\x00=\xcc\xcc\xcd\x00\x00~'
    >>> res=get_cmd_register_value(commandID['SET_VALUE'], StaticInput(1).current, 0.1)
    >>> print(encode(*res))
    b'~\x00\x10\x06Q\x00=\xcc\xcc\xcd\x00\x00~'
    >>> res=get_cmd_register_value('SET_VALUE', StaticInput(1).current, 0.1)
    >>> print(encode(*res))
    b'~\x00\x10\x06Q\x00=\xcc\xcc\xcd\x00\x00~'

    You can see these results are the same, thus any of these methods are valid.
    """
    # Convert command to hex if needed
    if type(command) is str:
        try:
            cmd_id = commandID[command]
        except KeyError:
            print("Unknown Command: {}".format(command))
            print("Valid Commands: {}".format(list(commandID.keys())))
            return None, None, None
    else:
        cmd_id = command

    # Convert command to multiple if needed
    if type(register) is list:
        if cmd_id == commandID['SET_VALUE']:
            cmd_id = commandID['SET_MULTIPLE']
        elif cmd_id == commandID['GET_VALUE']:
            cmd_id = commandID['GET_MULTIPLE']

    # Use register_tables if needed
    if type(value) in [UnitType, WaveformShape]:
        value = value.value

    # int32 and float64 are not captured by int and float, so we first convert to them
    if type(value) is np.int32:
        value = int(value)
    if type(value) is np.float64:
        value = float(value)

    # for setting manager value to a stage for a given channel & system
    if type(value) not in (int, list, bool, float, type(None)):
        if type(value) is str:
            found = False
            for key, field in list(register['range'].items()):
                if found:
                    break
                if field.lower().upper() == value.lower().upper():
                    found = True
                    break
            if found:
                value = key
        else:
            try:
                value = value.sys_id
            except AttributeError:
                print("Invalid System")
                return SimpleResponses['UNRECOGNIZED_MESSAGE']

    # set multiple with one value input
    if value is not None:
        if type(value) in (int, float, type(None)) and type(register) is list and len(register) > 1:
            value_list = []
            for i in range(len(register)):
                try:
                    if type(register[i]['type']) is int:
                        value_list.append(int(value))
                    elif type(register[i]['type']) is float:
                        value_list.append(float(value))
                    else:
                        value_list.append(int(value))
                except:
                    value_list.append(float(value))
            value = value_list

    # # handle various registers input types # #
    if type(register) in (int, list):
        # raw, raws or dicts
        if type(register) is list:
            # raws or dicts
            if all(isinstance(x, int) for x in register):
                # raws
                cmd_id, register_id = (cmd_id, register) if len(register) <= 8 else (None, None)
            else:
                # dicts
                if value is not None:
                    for i in range(len(value)):
                        if type(value[i]) is str:
                            found = False
                            for key, field in list(register[i]['range'].items()):
                                if found:
                                    break
                                if field.lower().upper() == value[i].lower().upper():
                                    found = True
                                    break
                            if found:
                                value[i] = key
                        elif type(value[i]) in [UnitType, WaveformShape]:
                            value[i] = value[i].value

                register_id = process_registers(register, value)
        else:
            # raw
            register_id = register
    else:
        # dict
        register_id = process_registers(register, value)
        if register_id is None:
            return None, None, None

    return (cmd_id, register_id, value) if register_id else (None, None, None)


def _set_internal(register: dict, response_data, value):
    """
    Currently unused.
    Intended for setting register['value'], such that state could be stored in a log file.
    :param register:
    :param response_data:
    :param value:
    :return:
    """
    if isinstance(value, list):
        value = value[0]
    while isinstance(response_data, list):
        while len(response_data) > 1:
            response_data = response_data.pop()
        if len(response_data) == 1:
            response_data = response_data[0]
        elif len(response_data) == 0:
            break

    if (value is None) and (response_data is None):
        register['value'] = None
    elif value == [] or value is None:
        register['value'] = response_data
    else:
        register['value'] = value