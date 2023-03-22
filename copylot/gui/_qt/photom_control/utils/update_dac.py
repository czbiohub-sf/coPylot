from collections.abc import Iterable
from copylot.gui._qt.photom_control.utils.show_error import show_dac_error
try:
    from mcculw import ul
    demo_mode = False
except ValueError:
    demo_mode = True
    print('Running in the UI demo mode. (from update_dac)')


def signal_to_galvo(
        ao_range,
        values,
        value_range=(0, 10),  # range of cordinates
        Vout_range=(-10, 10),  # range of output voltage
        dac_ch_x=0,
        dac_ch_y=1,
        board_num=0,
        invert=False,
):
    output_value = value_converter(values, value_range, Vout_range, invert)
    if demo_mode:
        print(f'DEMO mode: {output_value} is sent to ch{(dac_ch_x, dac_ch_y)}.')
    else:
        raw_valueX = ul.from_eng_units(board_num, ao_range, output_value[0])
        raw_valueY = ul.from_eng_units(board_num, ao_range, output_value[1])
        print(f'Real mode: {output_value} is sent to ch{(dac_ch_x, dac_ch_y)}.')
        try:
            ul.a_out(board_num, dac_ch_x, ao_range, raw_valueX)
            ul.a_out(board_num, dac_ch_y, ao_range, raw_valueY)
        except ul.ULError as e:
            _ = show_dac_error(e)


def signal_to_dac(
        ao_range,
        value,
        value_range=(0, 5),  # range of output laser power
        Vout_range=(0, 5),  # range of output voltage
        dac_ch=2,
        board_num=0,
        invert=False,
):
    output_value = value_converter(value, value_range, Vout_range, invert=invert)[0]
    if demo_mode:
        print(f'DEMO mode: {output_value} is sent to ch{dac_ch}.')
    else:
        raw_valueX = ul.from_eng_units(board_num, ao_range, output_value)
        print(f'Real mode: {output_value} is sent to ch{dac_ch}.')
        try:
            ul.a_out(board_num, dac_ch, ao_range, raw_valueX)
        except ul.ULError as e:
            _ = show_dac_error(e)


def value_converter(
        input_values,
        input_range,
        output_range,
        invert=False,
):
    if not isinstance(input_values, Iterable):
        input_values = [input_values]
    return [converter(normalizer(i, input_range), output_range, invert) for i in input_values]


def normalizer(x, input_range):
    return (x - min(input_range)) / abs(input_range[1] - input_range[0])


def converter(x, output_range, invert=False):
    if invert:
        return max(output_range) - x * abs(output_range[1] - output_range[0])
    else:
        return x * abs(output_range[1] - output_range[0]) + output_range[0]

