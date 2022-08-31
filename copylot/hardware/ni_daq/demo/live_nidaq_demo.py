import time

from copylot.hardware.ni_daq.live_nidaq import LiveNIDaq


def constant_voltage_single_channel_demo():
    # First create a LiveNIDaq object
    live_nidaq = LiveNIDaq()

    """
    Set the active analog channels you want to use.
    If you get an error in the following line, make sure
    your daq system and channels are correct.
    """
    live_nidaq.add_active_ao_channel("cDAQ1AO/ao0")
    live_nidaq.add_active_ao_channel("cDAQ1AO/ao1")

    # Set desired voltages to active ao_channels
    live_nidaq.set_constant_ao_voltage("cDAQ1AO/ao0", 0.2)
    live_nidaq.set_constant_ao_voltage("cDAQ1AO/ao1", 0.4)

    # Keep the desired voltages on for desired time in seconds, (5 seconds for our demo)
    time.sleep(50)

    # Clean the ao channels
    live_nidaq.zero()


if __name__ == '__main__':
    constant_voltage_single_channel_demo()
