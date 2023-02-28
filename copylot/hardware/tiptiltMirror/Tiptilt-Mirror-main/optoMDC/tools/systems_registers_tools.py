from optoKummenberg.tools.systems_registers_tools import *


def list_systems():
    """
    Inspect generic_registers for all imported and defined Systems.
    :return: list of System names
    """
    all_systems = inspect.getmembers(sys.modules['optoMDC.registers.xpr4_registers'], inspect.isclass)
    return [system[0] for system in all_systems if hasattr(system[1](0), '_is_a_system')]


def get_register(system_name: str, register_name, channel: int = 0):
    """
    Given a System name and Register name, will return the associated register_id integer
    :param system_name: str
    :param register_name: str
    :param channel: int
    :return: int register_id
    """
    registers = inspect.getmembers(sys.modules['optoMDC.registers.xpr4_registers'], inspect.isclass)
    register_system = dict(registers)[system_name](channel)
    register_list = inspect.getmembers(register_system)
    register_id = dict(register_list)[register_name]
    return register_id