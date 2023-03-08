import inspect
import sys
import inflect
from ..registers.ClassAbstracts import System

# # Currently not configured, must pull all classes from registers module
# def system_names():
#     all_systems = inspect.getmembers(sys.modules[__name__], inspect.isclass)
#     return [system[0] for system in all_systems if system[1]()._is_a_system]


def list_systems():
    """
    Inspect generic_registers for all imported and defined Systems.
    :return: list of System names
    """
    all_systems = inspect.getmembers(sys.modules['optoKummenberg.registers.generic_registers'], inspect.isclass)
    return [system[0] for system in all_systems if hasattr(system[1](0), '_is_a_system')]


def get_register(system_name: str, register_name, channel: int = 0):
    """
    Given a System name and Register name, will return the associated register_id integer
    :param system_name: str
    :param register_name: str
    :param channel: int
    :return: int register_id
    """
    registers = inspect.getmembers(sys.modules['optoKummenberg.registers.generic_registers'], inspect.isclass)
    register_system = dict(registers)[system_name](channel)
    register_list = inspect.getmembers(register_system)
    register_id = dict(register_list)[register_name]
    return register_id


def get_registers(system_name: str, channel: int = 0):
    """
    Returns list of tuples containing registers name and dictionary.
    :param system_name:
    :param channel:
    :return:
    """
    if inspect.isclass(system_name):
        if issubclass(system_name, System):
            system_object = system_name()
    else:
        all_systems = inspect.getmembers(sys.modules['optoKummenberg.registers.generic_registers'], inspect.isclass)
        system_object = dict(all_systems)[system_name](channel)

    attributes = inspect.getmembers(system_object, lambda a: not (inspect.isroutine(a)))
    register_list = [item for item in attributes if type(item[1]) is dict
                     and not (item[0].startswith('__') and item[0].endswith('__'))]

    return dict(register_list)


def process_registers(register_fields: dict, values):
    r"""
    Gives validity of registers field values to be set, and returns command and registers(s) IDs.

    Parameters
    ----------
    register_fields : dict
        The dictionary containing registers information.
    values
        The desired value(s) to set the registers.

    Returns
    -------
    command_id : int
        Command ID necessary to send single or multiple registers settings.
    register_id : int
        Register ID corresponding to given registers.

    Raises
    ------
    Returns None in case of parse_error (value out of range, or invalid input)

    See Also
    --------
    Register fields are returned by registers class attributes, see registers.

    """
    if isinstance(register_fields, list):
        if len(register_fields) > 8:
            print('Cannot Process more than 8 registers at once.')
            return None

        if values is None:
            pass
        else:
            if not isinstance(values, list):
                value_list = []
                for _ in range(len(register_fields)):
                    value_list.append(values)
                values = value_list
            if len(register_fields) != len(values):
                print("Number of Registers is Less Than Number of Values!")
                return None

        for i in range(len(register_fields)):
            if values is None:
                pass
            elif not is_valid_value(register_fields[i], values[i]):
                # invalid value sent!
                invalid_number = inflect.engine().ordinal(i + 1)
                print('Invalid value for {} given registers'.format(invalid_number))
                valid_range = register_fields[i]['range']
                print('Given Value: {}. Valid Range: {}'.format(values, valid_range))
                return None
        register_id = [field['id'] for field in register_fields]
    else:
        if values is None:
            # get command
            pass
        elif not is_valid_value(register_fields, values):
            # invalid value sent!
            print('Invalid value for given registers')
            valid_range = register_fields['range']
            print('Given Value: {}. Valid Range: {}'.format(values, valid_range))
            return None
        register_id = register_fields['id']
    return register_id


def is_valid_channel(value):
    r"""
    Given a channel number value, determines if value is within accepted parameters.

    Parameters
    ----------
    value
        Must be between 0 and 8, can be int float or string

    """
    if type(value) in (int, float, str):
        if type(value) is int:
            return 0 <= value <= 8
        elif type(value) is float:
            return value.is_integer() and 0 <= value <= 8
        else:
            try:
                return 0 <= int(value) <= 8
            except:
                return False
    else:
        return False


def is_valid_value(register_dict, value):
    r"""
    Given a registers record and a value, determines if value is within accepted parameters.

    Parameters
    ----------
    register_dict : dict
        Register dictionary fields corresponding to desired registers.{'id': registers number, 'type': data type, ...}
    value : varies
        Value to set given registers.
    Raises
    ------
    none

    Notes
    -----
    Valid inputs follow the following logic table.

    +------------------------+-------------+-------------+------------+------------+
    | Input Value            | Register    | Register    | Register   | Register   |
    |                        | Type: int   | Type: float | Type: bool | Type: None |
    +========================+=============+=============+============+============+
    | int                    | check range | check range | is binary? | False      |
    +------------------------+-------------+-------------+------------+------------+
    | float                  | check range | check range | is binary? | False      |
    +------------------------+-------------+-------------+------------+------------+
    | bool                   | False       | False       | True       | False      |
    +------------------------+-------------+-------------+------------+------------+
    | None                   | False       | False       | False      | True       |
    +------------------------+-------------+-------------+------------+------------+
    | Other                  | False       | False       | False      | False      |
    +------------------------+-------------+-------------+------------+------------+

    Additional Notes
    ----------------
    Validation for requests to set values in the Signal Flow Manager are slightly different.
    The channel you are setting must match the channel in the flow manager.
    For example, it would not make sense to set the Input channel 0 to SPI channel 2, etc.
    """
    # TODO: Add list type for discrete ranges, specifically for SystemID range.
    try:
        value_type = type(value)
        register_type = register_dict['type']
        register_id = register_dict['id']
        register_range = register_dict['range']
        is_flow_manager = register_dict['unit'] == 'SystemID'
    except:
        return False

    if type(register_range) is dict:
        register_range = list(register_range.keys())

    if is_flow_manager:
        try:
            value = value.sys_id
        except:
            if value_type is not int:
                return False

        channel_id = (register_id & 0x00ff)//5
        if channel_id in [value % 8]:
            return True
        else:
            return False

    def range_check(val, valid_range):
        return valid_range[0] <= val <= valid_range[-1]

    if register_type is int:
        if value_type in (int, float):
            if value_type is int:
                if register_range is None:
                    return True
                else:
                    return range_check(value, register_range)
            if value_type is float:
                if value.is_integer():
                    if register_range is None:
                        return True
                    else:
                        return range_check(value, register_range)
                else:
                    return False
        elif value_type is bool:
            return value in (True, False)
        else:
            return False

    if register_type is float:
        if value_type in (int, float):
            if register_range is None:
                return True
            return range_check(value, register_range)
        else:
            return False

    if register_type is bool:
        return value in (True, False)

    if register_type is None:
        return value_type is None