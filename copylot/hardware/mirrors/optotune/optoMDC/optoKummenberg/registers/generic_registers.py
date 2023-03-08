r"""
Lookup tables / management of System registers.

Each System is represented by its own class, with Registers as attributes of that class.
The registers module can be imported to retrieve information about a given registers.
Syntax is as follows: registers.SYSTEM_NAME(CHANNEL_NUMBER).REGISTER_NAME

Returns
-------
dict
    A standard lookup will return a Register Record, or dictionary, containing pertinent registers information.

Notes
-----
A handful of helper methods are included to manage registers requests. See corresponding info for the following:
    is_valid_channel(value), is_valid_value(register_dict, value)
    encode(command_id. register_id)
    system_info()
    system_names()
    register_names(system_name)
    get_register_id(system_name, register_name, _channel)
    parse_error(error_code)
    help()

Examples
--------

For example, this imports the registers module, and collects the registers record of USB channel 0, as well as the
registers record for setting the input channel system of the Signal Flow Manager.

    >>> import optoKummenberg
    >>> optoKummenberg.Registers.StaticInput(0).of

    >>> reg.StaticInput(0).of
    {'id': 20737, 'type': <class 'float'>, 'unit': None, 'range': [-1, 1], 'default': 0.0}
    >>> reg.Manager(0).input
    {'id': 16384, 'type': <class 'int'>, 'unit': 'SystemID', 'range': None, 'default': None}
    >>> optoKummenberg.tools.systems_registers_tools.is_valid_value(registers.StaticInput.angle, 22.1)
    True

Additional Notes
----------------
For more info on a given registers, see the help text in the corresponding System class.
This will display ID, Data Type, Units, Range, Default Value, and Comments.
    >>> registers.SignalGenerator.help()

For a complete list of Systems, call one of the helper methods from registers module itself.
    >>> optoMDC.tools.systems_registers_tools.system_names()
    >>> optoMDC.tools.systems_registers_tools.system_info()

"""
# other
import inspect
import sys
from ..tools.definitions import CHANNEL_CNT
from ..tools.systems_registers_tools import get_registers
# input stage
from .InputStage import *
# input conditoning
from .InputConditioning import *
# control mode
from .ControlStage import *
# output conditioning
from .OutputConditioning import *
# output
from .OutputStage import *
# misc systems
from .MiscSystems import *


def help():
    print(__doc__)


def systems():
    all_systems = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    all_systems = list(zip(*all_systems))[1]
    sys_dict = {}
    for system in all_systems:
        try:
            for i in range(CHANNEL_CNT):
                sys_obj = system(channel=i)
                sys_id = sys_obj.sys_id
                reg_dict = dict(sys_obj.register_list)
                sys_dict.update({sys_id: {'name': sys_obj.name, 'registers': reg_dict}})
        except TypeError:
            # not a system
            pass
        except AttributeError:
            # abstract system, do not add to list
            pass
    return sys_dict
    # return [system for system in all_systems if system()._is_a_system]
