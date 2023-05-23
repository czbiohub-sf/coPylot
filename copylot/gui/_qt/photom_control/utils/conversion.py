from collections.abc import Iterable
from copylot.gui._qt.photom_control.utils.show_error import show_dac_error
from copylot import logger


## TODO: check and implement when we use a DAC
# try:
#     from mcculw import ul
#     demo_mode = False
# except ValueError:
#     demo_mode = True
#     logger.debug('Running in the UI demo mode. (from conversion.py)')


# def signal_to_galvo(
#         ao_range,
#         values,
#         value_range=(0, 10),  # range of cordinates
#         Vout_range=(-10, 10),  # range of output voltage
#         dac_ch_x=0,
#         dac_ch_y=1,
#         board_num=0,
#         invert=False,
# ):
#     output_value = value_converter(values, value_range, Vout_range, invert)
#     if demo_mode:
#         print(f'DEMO mode: {output_value} is sent to ch{(dac_ch_x, dac_ch_y)}.')
#     else:
#         raw_valueX = ul.from_eng_units(board_num, ao_range, output_value[0])
#         raw_valueY = ul.from_eng_units(board_num, ao_range, output_value[1])
#         print(f'Real mode: {output_value} is sent to ch{(dac_ch_x, dac_ch_y)}.')
#         try:
#             ul.a_out(board_num, dac_ch_x, ao_range, raw_valueX)
#             ul.a_out(board_num, dac_ch_y, ao_range, raw_valueY)
#         except ul.ULError as e:
#             _ = show_dac_error(e)


# def signal_to_dac(
#         ao_range,
#         value,
#         value_range=(0, 5),  # range of output laser power
#         Vout_range=(0, 5),  # range of output voltage
#         dac_ch=2,
#         board_num=0,
#         invert=False,
# ):
#     output_value = value_converter(value, value_range, Vout_range, invert=invert)[0]
#     if demo_mode:
#         print(f'DEMO mode: {output_value} is sent to ch{dac_ch}.')
#     else:
#         raw_valueX = ul.from_eng_units(board_num, ao_range, output_value)
#         print(f'Real mode: {output_value} is sent to ch{dac_ch}.')
#         try:
#             ul.a_out(board_num, dac_ch, ao_range, raw_valueX)
#         except ul.ULError as e:
#             _ = show_dac_error(e)


def value_converter(input_values, input_range, output_range, invert=False):
    """
    Converts input values from the input range to the output range.

    Args:
        input_values (iterable or float): The input value(s) to be converted.
        input_range (tuple): A tuple containing the minimum and maximum values of the input range.
        output_range (tuple): A tuple containing the minimum and maximum values of the output range.
        invert (bool, optional): Specifies whether to perform an inverse conversion. Default is False.

    Returns:
        list: A list of converted values.

    """
    if not isinstance(input_values, Iterable):
        input_values = [input_values]
    return [converter(normalizer(i, input_range), output_range, invert) for i in input_values]


def normalizer(x, input_range):
    """
    Normalizes a value based on the input range.

    Args:
        x (float): The value to be normalized.
        input_range (tuple): A tuple containing the minimum and maximum values of the input range.

    Returns:
        float: The normalized value.

    """
    return (x - min(input_range)) / abs(input_range[1] - input_range[0])


def converter(x, output_range, invert=False):
    """
    Converts a normalized value to the corresponding value in the output range.

    Args:
        x (float): The normalized value to be converted.
        output_range (tuple): A tuple containing the minimum and maximum values of the output range.
        invert (bool, optional): Specifies whether to perform an inverse conversion. Default is False.

    Returns:
        float: The converted value.

    """
    if invert:
        return max(output_range) - x * abs(output_range[1] - output_range[0])
    else:
        return x * abs(output_range[1] - output_range[0]) + output_range[0]
