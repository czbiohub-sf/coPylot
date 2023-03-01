from enum import IntEnum

# Kummenberg Internal Definitions
MAX_PAYLOAD_SIZE    = 50
SAMPLING_FREQ = 10000
ENDIAN = ">"
CHANNEL_CNT = 4
MAX_CHANNEL_CNT = 8
SIGNAL_FLOW_STAGE_CNT = 5
CMD_DELAY = 0.05
CHUNK_SIZE = 10
ESCAPE_BYTE = 0x7D
FRAME_BOUNDARY = 0x7E
ESCAPE_MASK = 1 << 5

SimpleResponses = {
    'PROCESSED_WITHOUT_ERROR' : b'OK\r\n',
    'OUT_OF_RANGE_UPPER'      : b'OU\r\n',
    'OUT_OF_RANGE_LOWER'      : b'OL\r\n',
    'UNRECOGNIZED_MESSAGE'    : b'NO\r\n',
    'ERROR'                   : b'ERROR\r\n'
}


class CommandID:
    GENERIC_COMMAND = 0x00
    GET_FIRMWARE_ID = 0X01
    GET_STATUS      = 0X02
    START_SELF_TEST = 0X03
    LOAD_CONFIG     = 0X04
    STORE_CONFIG    = 0X05
    SET_COMM_MODE   = 0X06
    SET_VALUE       = 0X10
    GET_VALUE       = 0X11
    SET_MULTIPLE    = 0X12
    GET_MULTIPLE    = 0X13
    SET_VECTOR      = 0X14
    GET_VECTOR      = 0X15

commandID = {
            'GENERIC_COMMAND' : 0X00,
            'GET_FIRMWARE_ID' : 0X01,
            'GET_STATUS'      : 0X02,
            'START_SELF_TEST' : 0X03,
            'LOAD_CONFIG'     : 0X04,
            'STORE_CONFIG'    : 0X05,
            'SET_COMM_MODE'   : 0X06,
            'SET_VALUE'       : 0X10,
            'GET_VALUE'       : 0X11,
            'SET_MULTIPLE'    : 0X12,
            'GET_MULTIPLE'    : 0X13,
            'SET_VECTOR'      : 0X14,
            'GET_VECTOR'      : 0X15
            }
commandName = dict((value, key) for key, value in commandID.items())


class UnitType(IntEnum):
    CURRENT   = 0
    OF        = 1
    XY     = 2
    UNDEFINED = 3


class Units:
    CURRENT     = 0
    OF          = 1
    XY          = 2
    UNDEFINED   = 3


class WaveformShape(IntEnum):
    SINUSOIDAL  = 0
    TRIANGULAR  = 1
    RECTANGULAR = 2
    SAWTOOTH    = 3
    PULSE       = 4


class Waveforms:
    SINUSOIDAL  = 0
    TRIANGULAR  = 1
    RECTANGULAR = 2
    SAWTOOTH    = 3
    PULSE       = 4