import struct
from ..tools.definitions import ENDIAN, FRAME_BOUNDARY, ESCAPE_BYTE, ESCAPE_MASK, CommandID


def parse_error_flags(error_flag_data: int):
    r"""
    Parses error flag register values. Given error number, returns error string.

    Parameters
    ----------
    error_flag_data : int
        Error code hex number, will convert if string.

    Returns
    -------
    code: str
        Error code dictionary.
    """
    bits = format(error_flag_data[0], '#032b')[2::]
    error_result = {
        'Proxy Disconnected': bool(int(bits[29])),
        'Proxy Temperature Threshold Reached': bool(int(bits[28])),
        'Mirror Temperature Threshold Reached': bool(int(bits[27])),
        'Mirror EEPROM Invalid': bool(int(bits[26])),
        'Mirror Unstable': bool(int(bits[25])),
        'Linear Output Limit Reached': bool(int(bits[24])),
        'Linear Output Average Limit Reached': bool(int(bits[23])),
        'XY Input Trimmed': bool(int(bits[22])),
        'Proxy Was Disconnected': bool(int(bits[21])),
        'Proxy Temperature Threshold Was Reached': bool(int(bits[20])),
        'Mirror Temperature Threshold Was Reached': bool(int(bits[19])),
        'Linear Output Limit Was Reached': bool(int(bits[18])),
        'Linear Output Average Limit Was Reached': bool(int(bits[17])),
        'XY Input Was Trimmed': bool(int(bits[16])),
        'Reserved': bits[0:16]
    }

    return error_result


def parse_error(error_code: int):
    r"""
    Given error number, returns error string.

    Parameters
    ----------
    error_code : int
        Error code hex number, will convert if string.

    Examples
    --------
    Return error information from _board

    Returns
    -------
    code: str
        Error code string.

    >>> parse_error(0x0001)
    'COMMAND_LENGTH_MISMATCH'
    >>> parse_error('1')
    'COMMAND_LENGTH_MISMATCH'

    """

    error_codes = {
        0x0001:	'FRAME_INVALID',
        0x0002:	'COMMAND_UNKNOWN',
        0x0003:	'COMMAND_LENGTH_MISMATCH',
        0x0004:	'CRC_FAIL',
        0x0005:	'COMMAND_NOT_IMPLEMENTED_YET',

        0x0101:	'REGISTER_DOES_NOT_EXIST',
        0x0102:	'REGISTER_WRITE_UNSUCCESSFUL',
        0x0103:	'REGISTER_VALUE_OUT_OF_RANGE',
        0x0104:	'REGISTER_IS_NOT_VALID',
        0x0105: 'REGISTER_READ_UNSUCCESSFUL',
        0x0106: 'REGISTER_IS_READ_ONLY',
        0x0107: 'VECTOR_INDEX_OUT_OF_RANGE',
        0x0108: 'VECTOR_INDEX_NOT_ALIGNED',
        0x0109: 'REGISTER_IS_LOCKED',
        0x010a: 'REGISTER_IS_NOT_READABLE',

        0x0201:	'SYSTEM_DOES_NOT_EXIST',
        0x0202:	'SYSTEM_NOT_A_VALID_SELECTION',
        0x0203:	'CHAIN_CONSTRUCTION_ERROR',

        0x0701:	'ERROR_FLAG_NO_SNAPSHOT_VALUES_AVAILABLE_TO_LOAD',
        0x0702: 'ERROR_FLAG_CANNOT_SAVE_SNAPSHOT',
        0x0703: 'ERROR_FLAG_CORRUPTED_SNAPSHOT',
        0x0704: 'ERROR_FLAG_SNAPSHOT_INDEX_OUT_OF_RANGE',
        0x0705: 'ERROR_FLAG_NOT_ENOUGH_SPACE_FOR_SNAPSHOT',
        0x0f0f: 'COMMUNICATION_ERROR',
        0xffff: 'WRONG_BOARD_MODE_FOR_COMMAND'
        }
    code = 'UNKNOWN_ERROR_CODE'
    try:
        code = error_codes[int(error_code)]
    finally:
        return code


def encode(command_id, register_id, data=None):
    r"""
    Given command_id, register_id and payload, will determine proper bytestring to transmit.
    Uses the following format:

    +----------+---------------------+---------+-----------+------------+---------------+----------+
    | Frame    | Reserved            | Command | Data size | Data       | CRC           | Frame    |
    | Boundary | slave address: 0x00 |         |           | payload    | if applicable | Boundary |
    +==========+=====================+=========+===========+============+===============+==========+
    | 1 byte   | 1 byte              | 1 byte  | 1 byte    | 0-50 bytes | 2 bytes       | 1 byte   |
    +----------+---------------------+---------+-----------+------------+---------------+----------+

    Parameters
    ----------
    command_id
        Identifier corresponding to command
    register_id
        Identifier corresponding to register. See register['id'] field.
    data
        Float or int or bytes, depending on the type of register

    Raises
    ------
    none

    Returns
    -------
    b_message: bytearray
        Stuffed and escaped bytestring, following protocol above.

    Notes
    -----
    Given a FRAME_BOUNDARY of 0x7e and ESCAPE_BYTE of 0x7d, every appearance of the bytes 0x7e or 0x7d in the data
    (so in a role other than the delimiter or the escape byte)  is replaced by the sequence 0x7d 0x5e or 0x7d 0x5d,
    respectively. This follows ESCAPE_MASK = 1 << 5, or 0x20, thus the byte is XOR'd with the mask and prepended by 0x7d
    """
    b_header = b''
    b_message = b''
    b_delimiter = struct.pack(">B", 0x7E)
    b_slave_address = struct.pack(">B", 0x00)
    b_crc = struct.pack(">H", 0x00)
    b_cocommand_id = struct.pack(">B", command_id)
    if isinstance(register_id, list):  # Used for multiple values commands
        b_register_id = struct.pack(">H", len(register_id))
        for x in register_id:
            b_register_id += struct.pack(">H", x)
        if data is None:  # get values command
            size = 2 + 2 * len(register_id)
            b_header = b_slave_address + b_cocommand_id + struct.pack(">B", size)
            b_message = b_delimiter + b_header + b_register_id + b_crc + b_delimiter
        else:  # set values command
            size = 2 + 2 * len(register_id) + 4 * len(data)
            b_header = b_slave_address + b_cocommand_id + struct.pack(">B", size)
            b_data = b''
            for v in data:
                if isinstance(v, float):
                    b_data += struct.pack(">f", v)
                elif isinstance(v, int):
                    b_data += struct.pack(">i", v)
            b_message = b_delimiter + b_header + b_register_id + b_data + b_crc + b_delimiter
    else:  # Used for set get value and vector
        b_register_id = struct.pack(">H", register_id)
        if data is not None:
            if isinstance(data, float):  # Used for set value, when value is float
                b_data = struct.pack(">f", data)
                b_header = b_slave_address + b_cocommand_id + struct.pack(">B", 0x06)
            elif isinstance(data, int):  # Used for set value, when value is float
                b_data = struct.pack(">i", data)
                b_header = b_slave_address + b_cocommand_id + struct.pack(">B", 0x06)
            elif isinstance(data, list):  # Used for get Vector
                if len(data) == 2:
                    b_data = struct.pack(">H", data[0]) + struct.pack(">B", data[1])  # Pack vector index and length
                    b_header = b_slave_address + b_cocommand_id + struct.pack(">B", 0x05)
            b_message = b_delimiter + b_header + b_register_id + b_data + b_crc + b_delimiter
        else:
            if command_id == 0x04 or command_id == 0x05:
                b_header = b_slave_address + b_cocommand_id + struct.pack(">B", 0x01)  # Payload contains 1 byte config ID
                b_message = b_delimiter + b_header + struct.pack(">B", register_id) + b_crc + b_delimiter
            else:
                b_header = b_slave_address + b_cocommand_id + struct.pack(">B", 0x02)  # Payload contains only registers ID
                b_message = b_delimiter + b_header + b_register_id + b_crc + b_delimiter
    b_message = b_message.replace(b'}', b'}]')
    b_message = b_message[1:-1].replace(b'~', b'}^')
    b_message = b'~' + b_message + b'~'

    return b_message


def encode_vector(register, index, vector):
    """
    Encodes the given register vector to bytes.

    Parameters
    ----------
    register : dict or int
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
        byte string to transmit.

    """
    cmd_id = CommandID.SET_VECTOR
    index = index * 4
    bstr = bytes([])

    if type(register) is int:
        # generic packing, vals must already be in correct format for transmission
        vals = struct.pack(ENDIAN + "f" * len(vector), *vector)
        data = struct.pack(ENDIAN + "HHB", register, index, len(vals)) + vals
    else:
        if register['type'] is int:
            # common, int32 values
            vals = struct.pack(ENDIAN + "i" * len(vector), *vector)
            data = struct.pack(ENDIAN + "HHB", register['id'], index, len(vals)) + vals
        elif register['type'] is float:
            # common, float32 values
            vals = struct.pack(ENDIAN + "f" * len(vector), *vector)
            data = struct.pack(ENDIAN + "HHB", register['id'], index, len(vals)) + vals
        elif register['type'] is bytes:
            # less common, generally for eeprom data
            vals = bytes(list(vector))
            data = struct.pack(ENDIAN + "HHB", register['id'], index // 4, len(vals)) + vals
        elif register['type'] is str:
            # uncommon, char values
            vals = struct.pack(ENDIAN + "c" * len(vector), *vector)
            data = struct.pack(ENDIAN + "HHB", register['id'], index // 4, len(vals)) + vals
        else:
            # generic stuffing due to unknown register['type'] value
            bstr = bytes([0, cmd_id, len(vector)] + list(vector))
            bstr = bstr + bytes((0, 0))

            def stuff(unstuffed):
                result = [FRAME_BOUNDARY]
                for b in unstuffed:
                    if b in (ESCAPE_BYTE, FRAME_BOUNDARY):
                        result.append(ESCAPE_BYTE)
                        result.append(b ^ ESCAPE_MASK)
                    else:
                        result.append(b)
                result.append(FRAME_BOUNDARY)
                return bytes(result)
            return stuff(bstr)

    # build packet frame and stuff bytes
    bstr = bytes([FRAME_BOUNDARY, 0, cmd_id, len(data)] + list(data) + [0, 0, FRAME_BOUNDARY])
    bstr = bstr.replace(bytes([ESCAPE_BYTE]), bytes([ESCAPE_BYTE, ESCAPE_BYTE ^ ESCAPE_MASK]))
    bstr = bstr[1:-1].replace(bytes([FRAME_BOUNDARY]), bytes([ESCAPE_BYTE, FRAME_BOUNDARY ^ ESCAPE_MASK]))
    bstr = b'~' + bstr + b'~'
    return bstr


def decode(data: bytes):
    r"""
    Given bytestring, will unpack/destuff values, following stuffing method described in Notes.

    Parameters
    ----------
    command_id
        Identifier corresponding to command
    register_id
        Identifier corresponding to register. See register['id'] field.

    Raises
    ------
    none

    Returns
    -------
    result: bytearray
        Destuffed bytestring, following protocol above.

    Notes
    -----
    Given a FRAME_BOUNDARY of 0x7e and ESCAPE_BYTE of 0x7d, every appearance of the bytes 0x7e or 0x7d in the data
    (so in a role other than the delimiter or the escape byte)  is replaced by the sequence 0x7d 0x5e or 0x7d 0x5d,
    respectively. This follows ESCAPE_MASK = 1 << 5, or 0x20, thus the byte is XOR'd with the mask and prepended by 0x7d
    """
    result = []
    try:
        if len(data) < 2 or data[0] != FRAME_BOUNDARY or data[-1] != FRAME_BOUNDARY:
            print('Byte De-stuffing Cannot Be Performed. [data={}]'.format(data))
            return None

        i = 1
        while i < (len(data) - 1):
            if data[i] == ESCAPE_BYTE:
                result.append(data[i + 1] ^ ESCAPE_MASK)
                i += 2
            else:
                result.append(data[i])
                i += 1
    except TypeError or KeyError:
        print('Byte De-stuffing Cannot Be Performed. [data={}]'.format(data))

    if FRAME_BOUNDARY in data[1:-1]:
        print("ERROR: Duplicate Frame Returned. System Reboot Required.")
        return None
    else:
        return bytes(result)
