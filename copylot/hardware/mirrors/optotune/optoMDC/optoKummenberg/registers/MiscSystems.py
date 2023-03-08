from .ClassAbstracts import System
from ..tools.parsing_tools import parse_error_flags
from ..tools.definitions import CHUNK_SIZE, UnitType
from ..tools.systems_registers_tools import get_registers
from warnings import warn


class Manager(System):
    r"""
The Signal Flow Channel Manager is managing the active systems in the signal flow chain.
System ID for channel X: 0x40

+---------------------+---------------+-------------+----------+--------------+---------------+--------------------+
| Register Name       | Id            | Type        | Unit     | Range        | Default       | Comment            |
+=====================+===============+=============+==========+==============+===============+====================+
| input               | 5xCHANNEL + 0 | uint 32-bit | SystemID | 0x48 to 0x7f |               |                    |
+---------------------+---------------+-------------+----------+--------------+---------------+--------------------+
| input_conditioning  | 5xCHANNEL + 1 | uint 32-bit | SystemID | 0x48 to 0x7f |               |                    |
+---------------------+---------------+-------------+----------+--------------+---------------+--------------------+
| control             | 5xCHANNEL + 2 | uint 32-bit | SystemID | 0x48 to 0x7f |               |                    |
+---------------------+---------------+-------------+----------+--------------+---------------+--------------------+
| output_conditioning | 5xCHANNEL + 3 | uint 32-bit | SystemID | 0x48 to 0x7f |               |                    |
+---------------------+---------------+-------------+----------+--------------+---------------+--------------------+
| output              | 5*CHANNEL + 4 | uint 32-bit | SystemID | 0x48 to 0x7f |               |                    |
+---------------------+---------------+-------------+----------+--------------+---------------+--------------------+

    """

    @staticmethod
    def help():
        print(Manager.__doc__)

    def __init__(self, channel: int = 0, board=None):
        self.sys_id = 0x40
        self._readonly = False

        # TODO: I could calculate valid range here from channel using bit math.
        self.input = {'id': self.sys_id << 8 | channel * 5 | 0x00,
                      'type': int,
                      'unit': 'SystemID',
                      'range': [0x48, 0x7f],
                      'default': None,
                      'value': None}
        self.input_conditioning = {'name': 'input_conditioning',
                                   'id': self.sys_id << 8 | channel * 5 | 0x01,
                                   'type': int,
                                   'unit': 'SystemID',
                                   'range': [0x48, 0x7f],
                                   'default': None,
                                   'value': None}
        self.control = {'name': 'control',
                        'id': self.sys_id << 8 | channel * 5 | 0x02,
                        'type': int,
                        'unit': None,
                        'range': None,
                        'default': None,
                        'value': None}
        self.output_conditioning = {'name': 'output_conditioning',
                                    'id': self.sys_id << 8 | channel * 5 | 0x03,
                                    'type': int,
                                    'unit': 'SystemID',
                                    'range': [0x48, 0x7f],
                                    'default': None,
                                    'value': None}
        self.output = {'name': 'output',
                       'id': self.sys_id << 8 | channel * 5 | 0x04,
                       'type': int,
                       'unit': 'SystemID',
                       'range': [0x48, 0xef],
                       'default': None,
                       'value': None}

        System.__init__(self, channel, board)
        self.name = self.__class__.__name__

    def CheckSignalFlow(self):
        # pull input, input_conditioning, control, output_conditioning, and output registers
        input_id = self.get_register('input')[0]
        icond_id = self.get_register('input_conditioning')[0]
        cntrl_id = self.get_register('control')[0]
        ocond_id = self.get_register('output_conditioning')[0]
        outpt_id = self.get_register('output')[0]
        # get input units
        if input_id in range(0x50, 0x60):
            # static input has no units register
            input_units = 'Static'
        else:
            inpt_units_register = get_registers(self._board.systems[input_id]['name'])['unit']
            input_units = UnitType(self._board.get_value(inpt_units_register)[0]).name

        # find corresponding system for input and mode for control
        flow_states = {'SignalFlowManager': {'name': self.name,
                                             'channel': self._channel},
                       'InputStage': {'name': self._board.systems[input_id]['name'],
                                      'channel': input_id & 0x0F % 8,
                                      'unit': input_units},
                       'InputConditioning': {'name': self._board.systems[icond_id]['name'],
                                             'channel': icond_id & 0x0F % 8},
                       'ControlStage': {'name': self._board.systems[cntrl_id]['name'],
                                        'channel': cntrl_id & 0x0F % 8},
                       'OutputConditioning': {'name': self._board.systems[ocond_id]['name'],
                                              'channel': ocond_id & 0x0F % 8},
                       'OutputStage': {'name': self._board.systems[outpt_id]['name'],
                                       'channel': outpt_id & 0x0F % 8},
                       }
        # warning if unit mismatch 'except static input'
        if not flow_states['InputStage']['unit'].lower() in flow_states['ControlStage']['name'].lower() \
                and input_id not in range(0x50, 0x60):
            warn("Input Units: {} Do Not Match Control Mode: {}".format(flow_states['InputStage']['unit'],
                                                                        flow_states['ControlStage']['name']),
                 RuntimeWarning)
        # warning if channel mismatch
        used_channels = [flow_states[item]['channel'] for item in flow_states]
        if not all([item == used_channels[0] for item in used_channels]):
            warn("Not all stages are set to the same channel.", RuntimeWarning)
        return flow_states


class Status(System):
    r"""
Device Functionality - Firmware Status
System ID: 0x10

+---------------------+------+-------------+---------+---------------------------------------+
| Register Name       | Id   | Type        | Default | Comment                               |
+=====================+======+=============+=========+=======================================+
| firmware_id         | 0x00 | float 32-bit|         |                                       |
+---------------------+------+-------------+---------+---------------------------------------+
| firmware_branch     | 0x01 | float 32-bit|         |                                       |
+---------------------+------+-------------+---------+---------------------------------------+
| fw_type             | 0x02 | float 32-bit|         |                                       |
+---------------------+------+-------------+---------+---------------------------------------+
| fw_version_major    | 0x03 | float 32-bit|         |                                       |
+---------------------+------+-------------+---------+---------------------------------------+
| fw_version_minor    | 0x04 | float 32-bit|         |                                       |
+---------------------+------+-------------+---------+---------------------------------------+
| fw_version_build    | 0x05 | float 32-bit|         |                                       |
+---------------------+------+-------------+---------+---------------------------------------+
| fw_version_revision | 0x06 | float 32-bit|         |                                       |
+---------------------+------+-------------+---------+---------------------------------------+
| error_flag_register | 0x07 | float 32-bit| 0       | See: Status Register Values Below     |
+---------------------+------+-------------+---------+---------------------------------------+
| proxy_fpga_version  | 0x08 | float 32-bit|         |                                       |
+---------------------+------+-------------+---------+---------------------------------------+
| cpu_fpga_version    | 0x09 | float 32-bit|         |                                       |
+---------------------+------+-------------+---------+---------------------------------------+

Status Register Values:

====== =================================================================
Bit#   Message
====== =================================================================
0      Proxy not connected
1      Proxy temperature threshold is reached. See TemperatureManager
2      Mirror temperature threshold is reached See TemperatureManager
3      Mirror EEPROM not valid
4      Mirror not stable. See stability criterion in OpticalFeedback
5      Linear output limit is reached. See LinearOutput
6      Linear output average limit is reached. See LinearOutput
7      XY input is trimmed. See InputConditioning
8      Proxy was disconnected
9      Proxy temperature threshold was reached
10     Mirror temperature threshold was reached
11     Linear output limit was reached
12     Linear output average limit was reached
13     XY input was trimmed
14..31 Reserved
====== =================================================================
    Write:
    Writing to this register resets all history error flags 8, 9, 10, 11, 12, 13
    """

    @staticmethod
    def help():
        print(Status.__doc__)

    _is_a_system = False

    def __init__(self, board=None):

        self.sys_id = 0x10

        self.firmware_id = {'id': self.sys_id << 8 | 0x00,
                            'type': int,
                            'unit': None,
                            'range': None,
                            'default': None,
                            'value': None}
        self.fw_branch = {'id': self.sys_id << 8 | 0x01,
                          'type': int,
                          'unit': None,
                          'range': None,
                          'default': None,
                          'value': None}
        self.fw_type = {'id': self.sys_id << 8 | 0x02,
                        'type': int,
                        'unit': None,
                        'range': None,
                        'default': None,
                        'value': None}
        self.fw_version_major = {'id': self.sys_id << 8 | 0x03,
                                 'type': int,
                                 'unit': None,
                                 'range': None,
                                 'default': None,
                                 'value': None}
        self.fw_version_minor = {'id': self.sys_id << 8 | 0x04,
                                 'type': int,
                                 'unit': None,
                                 'range': None,
                                 'default': None,
                                 'value': None}
        self.fw_version_build = {'id': self.sys_id << 8 | 0x05,
                                 'type': int,
                                 'unit': None,
                                 'range': None,
                                 'default': None,
                                 'value': None}
        self.fw_version_revision = {'id': self.sys_id << 8 | 0x06,
                                    'type': int,
                                    'unit': None,
                                    'range': None,
                                    'default': None,
                                    'value': None}
        self.error_flag_register = {'id': self.sys_id << 8 | 0x07,
                                    'type': int,
                                    'unit': None,
                                    'range': None,
                                    'default': None,
                                    'value': None}
        self.proxy_fpga_version = {'id': self.sys_id << 8 | 0x08,
                                   'type': int,
                                   'unit': None,
                                   'range': None,
                                   'default': None,
                                   'value': None}
        self.cpu_fpga_version = {'id': self.sys_id << 8 | 0x09,
                                 'type': int,
                                 'unit': None,
                                 'range': None,
                                 'default': None,
                                 'value': None}
        System.__init__(self, board=board)
        self.name = self.__class__.__name__

    def GetFirmwareID(self):
        return self.get_register('firmware_id')

    def GetFirmwareBranch(self):
        return self.get_register('fw_branch')

    def GetFirmwareType(self):
        return self.get_register('fw_type')

    def GetFirmwareVersionMajor(self):
        return self.get_register('fw_version_major')

    def GetFirmwareVersionMinor(self):
        return self.get_register('fw_version_minor')

    def GetFirmwareBuild(self):
        return self.get_register('fw_version_build')

    def GetFirmwareVersionRevision(self):
        return self.get_register('fw_version_revision')

    def GetProxyFPGAVersion(self):
        return self.get_register('proxy_fpga_version')

    def GetCPUFPGAVersion(self):
        return self.get_register('cpu_fpga_version')

    def GetErrorFlagRegister(self):
        response = self.get_register('error_flag_register')
        if response[0] is not None:
            error_flag_register = parse_error_flags(response)
            if self._board.verbose:
                print(error_flag_register)
            return error_flag_register
        else:
            return response

    def ResetErrorFlagRegister(self):
        return self.set_register('error_flag_register', 0)

    def GetFirmwareSN(self, index, count):
        register = {'id': self.sys_id << 8, 'type': str}
        return self._board.get_vector(register, index, count)

    def SetFirmwareSN(self, index, vector):
        register = {'id': self.sys_id << 8, 'type': str}
        return self._board.set_vector(register, index, vector)

    def GetGitHEADSHA1Vector(self, index, count):
        register = {'id': self.sys_id << 8 | 0x01, 'type': str}
        return self._board.get_vector(register, index, count)


class BoardEEPROM(System):
    r"""
Device Functionality - BoardEEPROM Read/Write
System ID: 0x20

+--------------------+------+-----------------------------------------------------------------------------------------+
| Register Name      | Id   | Comment                                                                                 |
+====================+======+=========================================================================================+
| lock               | 0x00 | write the key to unlock, anything else to lock.Key value: 0x3f4744f6 (float 0.778396)   |
+--------------------+------+-----------------------------------------------------------------------------------------+


    """

    @staticmethod
    def help():
        print(BoardEEPROM.__doc__)

    _is_a_system = False

    def __init__(self, board=None):
        self.sys_id = 0x20
        self.lock = {'id': self.sys_id << 8 | 0x00, 'type': float, 'unit': None, 'range': None, 'default': 0.0,
                     'value': 0.778396}
        self.register = {'id': self.sys_id << 8, 'type': bytes}
        System.__init__(self, board=board)
        self.name = self.__class__.__name__

    def _SetEEPROMSegment(self, index, vector):
        resp = self._board.set_vector(self.register, index, vector)
        return resp

    def _GetEEPROMSegment(self, index, count):
        return self._board.get_vector(self.register, index, count)

    def GetEEPROM(self, index, count):
        vec = bytearray([])
        end_index = index + count
        chunk_size_in_bytes = CHUNK_SIZE * 4
        for i in range(index, index + count, chunk_size_in_bytes):
            if i + chunk_size_in_bytes > end_index:
                aux = self._GetEEPROMSegment(i, count % chunk_size_in_bytes)
            else:
                aux = self._GetEEPROMSegment(i, chunk_size_in_bytes)
            vec += aux[0]

        return vec

    def SetEEPROM(self, index, vector):
        chunk_size_in_bytes = CHUNK_SIZE * 4
        for i in range(0, len(vector), chunk_size_in_bytes):
            aux = vector[i:i + chunk_size_in_bytes]
            self._SetEEPROMSegment(i + index, aux)
        return vector

    def EEPROMLockEnable(self, enable=True):
        if enable:
            return self.set_register('lock', 0.0)
        else:
            return self.set_register('lock', self.lock['value'])

    def VerifyEEPROM(self, index, vector):
        stored_eeprom = self.GetEEPROM(index, len(vector))
        return stored_eeprom == vector, stored_eeprom


class DeviceEEPROM(System):
    r"""
Device Functionality - DeviceEEPROM Read/Write
System ID: 0x21

+--------------------+------+-----------------------------------------------------------------------------------------+
| Register Name      | Id   | Comment                                                                                 |
+====================+======+=========================================================================================+
| lock               | 0x00 | write the key to unlock, anything else to lock.Key value: 0x3edeb7aa (float 0.434995)   |
+--------------------+------+-----------------------------------------------------------------------------------------+
    """

    @staticmethod
    def help():
        print(DeviceEEPROM.__doc__)

    _is_a_system = False

    def __init__(self, board=None):
        self.sys_id = 0x21
        self.lock = {'id': self.sys_id << 8 | 0x0a, 'type': float, 'unit': None, 'range': None, 'default': 0.0,
                     'value': 0.434995}
        self.reparse = {'id': self.sys_id << 8 | 0x0a, 'type': float, 'unit': None, 'range': None, 'default': 0.0,
                        'value': 0}
        self.register = {'id': self.sys_id << 8, 'type': bytes}
        System.__init__(self, board=board, channel=None)
        self.name = self.__class__.__name__

    def _SetEEPROMSegment(self, index, vector):
        resp = self._board.set_vector(self.register, index, vector)
        return resp

    def _GetEEPROMSegment(self, index, count):
        return self._board.get_vector(self.register, index, count)

    def GetEEPROM(self, index, count):
        vec = bytearray([])
        end_index = index + count
        chunk_size_in_bytes = CHUNK_SIZE * 4
        for i in range(index, index + count, chunk_size_in_bytes):
            if i + chunk_size_in_bytes > end_index:
                aux = self._GetEEPROMSegment(i, count % chunk_size_in_bytes)
            else:
                aux = self._GetEEPROMSegment(i, chunk_size_in_bytes)
            try:
                vec += aux[0]
            except (IndexError, TypeError):
                return vec

        return vec

    def SetEEPROM(self, index, vector):
        chunk_size_in_bytes = CHUNK_SIZE * 4
        for i in range(0, len(vector), chunk_size_in_bytes):
            aux = vector[i:i + chunk_size_in_bytes]
            self._SetEEPROMSegment(i + index, aux)
        return vector

    def EEPROMLockEnable(self, enable=True):
        if enable:
            return self.set_register('lock', 0.0)
        else:
            return self.set_register('lock', self.lock['value'])

    def VerifyEEPROM(self, index, vector):
        stored_eeprom = self.GetEEPROM(index, len(vector))
        return stored_eeprom == vector, stored_eeprom

    def ReparseEEPROM(self):
        return self.get_register('reparse')


class VectorPatternMemory(System):
    """
Device Functionality - Vector Pattern Memory
System ID: 0x26

+---------------------------+------+-------------+------+-------+---------+-------------------------------------------+
| Register Name             | Id   | Type        | Unit | Range | Default | Comment                                   |
+===========================+======+=============+======+=======+=========+===========================================+
| proxy_valid               | 0x00 |float 32-bit |None  |       |         |                                           |
+---------------------------+------+-------------+------+-------+---------+-------------------------------------------+
    """

    def __init__(self, board=None):
        System.__init__(self, board=board)
        self.name = self.__class__.__name__

    sys_id = 0x26
    _readonly = False

    proxy_valid = {'id': sys_id << 8 | 0x00,
                        'type': int,
                        'unit': None,
                        'range': [0, 1],
                        'default': False,
                        'value': False}
    vector = {'id': sys_id << 8, 'type': float}


    def SetPattern(self, index, vector):
        for i in range(0, len(vector), CHUNK_SIZE):
            aux = vector[i:i + CHUNK_SIZE]
            self.SetPatternSegment(i + index, aux)

    def GetPattern(self, index, count):
        vec = []
        # end_index = index + count
        if count < CHUNK_SIZE:
            return self.GetPatternSegment(index, count)
        iters = count // CHUNK_SIZE
        remainder = count % CHUNK_SIZE
        for i in range(iters):
            aux = self.GetPatternSegment(i * CHUNK_SIZE, CHUNK_SIZE)
            vec.extend(aux)
        if remainder:
            aux = self.GetPatternSegment(index + count - remainder, remainder)
            vec.extend(aux)
        return vec

    def SetPatternSegment(self, index, vector):
        return self._board.set_vector(self.vector, index, vector)

    def GetPatternSegment(self, index: int, count: int):
        response = self._board.get_vector(self.vector, index, count)
        # return list(struct.unpack('>'+'f'*count, response))
        return response

    def GetProxyValidity(self):
        return self.get_register('proxy_valid')

    def SaveVectorMemory(self):
        return self.set_register('proxy_valid', 0)

    # def MakeChangesPersistent(self):
    #     self._board.set_value(self.pattern_segment, 0)


class SnapshotManager(System):
    """
Device Functionality - Vector Pattern Memory
System ID: 0x26

+---------------------------+------+-------------+------+-------+---------+-------------------------------------------+
| Register Name             | Id   | Type        | Unit | Range | Default | Comment                                   |
+===========================+======+=============+======+=======+=========+===========================================+
| snapshot_capacity         | 0x00 |float 32-bit |None  |       | 2       |                                           |
+---------------------------+------+-------------+------+-------+---------+-------------------------------------------+
| default_snapshot          | 0x01 |float 32-bit |None  |       | 0       |                                           |
+---------------------------+------+-------------+------+-------+---------+-------------------------------------------+
    """

    def __init__(self, board=None):
        self.sys_id = 0x27
        self._readonly = False

        self.snapshot_capacity = {'id': self.sys_id << 8 | 0x00,
                                  'type': int,
                                  'unit': None,
                                  'range': None,
                                  'default': False,
                                  'value': False}
        self.default_snapshot = {'id': self.sys_id << 8 | 0x01,
                                 'type': int,
                                 'unit': None,
                                 'range': [0, 7],
                                 'default': False,
                                 'value': False}
        System.__init__(self, board=board)
        self.name = self.__class__.__name__

    def GetSnapShotCapacity(self):
        return self.get_register('snapshot_capacity')

    def GetDefaultSnapShot(self):
        return self.get_register('default_snapshot')

    def SetDefaultSnapShot(self, value):
        return self.set_register('default_snapshot', value)


#
# class READOUT:
#     r"""
# Currently Not Implemented...
# DeviceEEPROM readout, to return the following registers records as a list:
#
# register_name               id      type
# EEPROM_VERSION                0x00    uint 32-bit
# EEPROM_SUBVERSION           0x01    uint 32-bit
# PART_CONFIGURATION          0x02    uint 32-bit
# PART_CONFIGURATION_VERSION    0x03    uint 32-bit
# MAX_POSITIVE_CURRENT        0x04    uint 32-bit
# MAX_NEGATIVE_CURRENT        0x05    uint 32-bit
# TEMPERATURE_OFFSET_A        0x06    uint 32-bit
# TEMPERATURE_GRADIENT_A        0x07    uint 32-bit
# TEMPERATURE_OFFSET_B        0x08    uint 32-bit
# TEMPERATURE_GRADIENT_B        0x09    uint 32-bit
#
#     """
#
#     @staticmethod
#     def help():
#         print(READOUT.__doc__)
#
#     sys_id = 0x21
#     _is_a_system = False
#
#     def __init__(self, channel: int = 0):
#         self._readonly = True
#
#     registers = inspect.getmembers(DeviceEEPROM, lambda a: not (inspect.isroutine(a)))
#     READOUT = [item for item in registers if
#                not (item[0].startswith('__') and item[0].endswith('__') or item[0].islower())]