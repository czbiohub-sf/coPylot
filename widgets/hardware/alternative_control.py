import time

import nidaqmx
import numpy as np


class NIdaq:
    # Channel information
    ch_ao0 = "cDAQ1AO/ao0"  # scanning channel
    ch_ao1 = "cDAQ1AO/ao1"  # view switching
    ch_ao2 = "cDAQ1AO/ao2"  # view switching
    ch_ao3 = "cDAQ1AO/ao3"  # stripe reduction

    ch_ctr0 = "cDAQ1/_ctr0"  # for retrigger
    ch_ctr0_internal_output = "/cDAQ1/Ctr0InternalOutput"
    ch_ctr1 = "cDAQ1/_ctr1"  # for counting number of frames
    ch_ctr1_internal_output = "/cDAQ1/Ctr1InternalOutput"
    ch_ctr2 = "cDAQ1/_ctr2"  # idle
    ch_ctr3 = "cDAQ1/_ctr3"  # idle

    PFI0 = "/cDAQ1/PFI0"  # camera exposure input
    PFI1 = "/cDAQ1/PFI1"    # idle

    ch_dio0 = "cDAQ1DIO/port0/line0"  # 488 digital channel
    ch_dio1 = "cDAQ1DIO/port0/line1"  # 561 digital channel
    ch_dio2 = "cDAQ1DIO/port0/line2"  # bright field
    ch_dio3 = "cDAQ1DIO/port0/line3"  # idle
    ch_dio4 = "cDAQ1DIO/port0/line4"  # idle
    ch_dio5 = "cDAQ1DIO/port0/line5"  # idle
    ch_dio6 = "cDAQ1DIO/port0/line6"  # idle
    ch_dio7 = "cDAQ1DIO/port0/line7"  # idle

    # constants
    MAX_VOL = 10  # unit: v, maximum voltage of the ao channels
    MIN_VOL = -10  # unit: v, minimal voltage of the ao channels
    CONVERT_RATIO = 159  # unit: um / v, to convert from voltage to the scan distance of the galvo
    READOUT_TIME_FULL_CHIP = 0.01  # unit: second, the readout time of the full chip camera
    MAX_VERTICAL_PIXELS = 2048     # unit: pixels, maximal number of pixels along the vertical direction

    def __init__(
            self,
            parent,
            exposure: float,
            nb_timepoints: int,
            scan_step: float,
            stage_scan_range: float,
            *,
            vertical_pixels: int = 2048,    # unit: pixels, number of pixels along the vertical direction
            num_samples: int = 20,  # for timing
            offset_view1: float  = 1550,   # unit: um, offset needed for view1
            offset_view2: float  = 1650,   # unit: um, offset needed for view2
            view1_galvo1: float  = 4.2,    # unit: v, to apply on galvo 1 for view 1
            view1_galvo2: float  = -4.08,  # unit: v, to apply on galvo 2 for view 1
            view2_galvo1: float  = -4.37,  # unit: v, to apply on galvo 1 for view 2
            view2_galvo2: float  = 3.66,   # unit: v, to apply on galvo 2 for view 2
            stripe_reduction_range: float = 0.1,    # unit: v, to apply on glavo gamma to reduce stripe
            stripe_reduction_offset: float = 0.58  # unit: v, to apply on glavo gamma to reduce stripe
        ):
        """
        Constructor of NIDaq.

        Parameters
        ----------
        exposure : float
            Expose time. Its unit is seconds.
        nb_timepoints : int
            Number of timepoints. Number of stacks to acquire.
        scan_step : float
            Scanning step size. unit: um.
        stage_scan_range : float
            Total range of stage scanning. unit: um.
        readout_time : float
             Readout time of the camera for full chip, unit: second.

        # TODO: add missing docstrings for rest of the optional arguments.
        """
        self.stop_now = False

        self.parent = parent
        self.exposure = exposure
        self.nb_timepoints = nb_timepoints
        self.scan_step = scan_step
        self.stage_scan_range = stage_scan_range
        self.nb_slices = int(self.stage_scan_range / self.scan_step) # for scanning, plus 2 due to Flash4 camera
        self.readout_time = self.READOUT_TIME_FULL_CHIP * vertical_pixels / self.MAX_VERTICAL_PIXELS
        self.num_samples = num_samples
        self.sampling_rate = self.num_samples / self.exposure

        self.view1 = {
            "offset": offset_view1,
            "galvo1": view1_galvo1,
            "galvo2": view1_galvo2
        }

        self.view2 = {
            "offset": offset_view2,
            "galvo1": view2_galvo1,
            "galvo2": view2_galvo2
        }

        self.stripe_reduction_range = stripe_reduction_range
        self.stripe_reduction_offset = stripe_reduction_offset

        print("number of slices:", self.nb_slices)
        print("current sampling_rate is:", self.sampling_rate)

    def select_view(self, view_index: float) -> None:
        """
        select the views, by using the correct offset of the scanning gavlo and the voltages of the switching galvos
        """
        if view_index == 1:
            view = self.view1
        elif view_index == 2:
            view = self.view2
        else:
            raise ValueError("View is not supported")

        offset, galvo1, galvo2 = [key_value_pair[1] for key_value_pair in view.items()]

        offset_in_vol = self._offset_dis_to_vol(offset)
        data = [offset_in_vol, galvo1, galvo2]
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan(self.ch_ao0)
            task.ao_channels.add_ao_voltage_chan(self.ch_ao1)
            task.ao_channels.add_ao_voltage_chan(self.ch_ao2)
            task.write(data, auto_start=True)

        print("end of select_view method")

    def _offset_dis_to_vol(self, offset: float) -> float:
        """
        convert the offset of each view from um to voltage
        """
        return offset / self.CONVERT_RATIO - self.MAX_VOL

    def select_channel_remove_stripes(self, ch_index):
        if ch_index == 488:
            self.ch = self.ch_dio0
        elif ch_index == 561:
            self.ch = self.ch_dio1
        else:
            raise ValueError("Channel not supported!")

        nb_on_sample = round((self.exposure - self.readout_time) * self.sampling_rate)
        # nb_off_sample = round(self.readout_time * self.sampling_rate)
        self.data_do = [True] * nb_on_sample + [False] * (self.num_samples - nb_on_sample)

        self.task_do = nidaqmx.Task()
        self.task_do.do_channels.add_do_chan(self.ch)

        self.task_ao = nidaqmx.Task("ao0")
        self.task_ao.ao_channels.add_ao_voltage_chan(self.ch_ao3)
        # for stripe reduction
        stripe_min = -self.stripe_reduction_range + self.stripe_reduction_offset
        stripe_max = self.stripe_reduction_range + self.stripe_reduction_offset
        nb_on_sample = round((self.exposure - self.readout_time) * self.sampling_rate)
        nb_off_sample = round(self.readout_time * self.sampling_rate)
        self.data_ao3 = list(np.linspace(stripe_min, stripe_max, nb_on_sample))
        self.data_ao3.extend([stripe_min] * nb_off_sample)

        # was in other method
        self.task_do.timing.cfg_samp_clk_timing(rate=self.sampling_rate,
                                           source=self.ch_ctr0_internal_output,
                                           sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
        self.task_ao.timing.cfg_samp_clk_timing(rate=self.sampling_rate,
                                           source=self.ch_ctr0_internal_output,
                                           sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)

        self.task_ctr = self._set_up_retriggerable_counter(self.ch_ctr0)

        self.task_do.write(self.data_do)
        self.task_ao.write(self.data_ao3)
        self.task_do.start()
        self.task_ao.start()
        self.task_ctr.start()
        # time.sleep(0.5)
        print("type s to abort:")
        while not self.stop_now:
            time.sleep(0.05)

        print("in right place")

        self.task_do.stop()
        self.task_ao.stop()
        self.task_ctr.stop()
        self.task_ctr.close()
        self.task_do.close()
        self.task_ao.close()

        print("aborted")

        self.set_dio_state(self.ch, False)

        self.parent.signals.finished.emit()

    def _set_up_retriggerable_counter(self, counter):
        """set up a retriggerable counter task"""
        task_ctr = nidaqmx.Task()
        task_ctr.co_channels.add_co_pulse_chan_freq(counter,
                                                    idle_state=nidaqmx.constants.Level.LOW,
                                                    freq=self.sampling_rate)
        task_ctr.timing.cfg_implicit_timing(sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                            samps_per_chan=self.num_samples)
        task_ctr.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source=self.PFI0,
                                                                trigger_edge=nidaqmx.constants.Slope.RISING)
        task_ctr.triggers.start_trigger.retriggerable = True
        return task_ctr

    def set_dio_state(self,ch, value):
        """set a DIO channel,
        false to low, true to high"""
        with nidaqmx.Task() as task:
            task.do_channels.add_do_chan(ch)
            task.write([value], auto_start=True)


if __name__ == "__main__":
    daq_card = NIdaq(
            exposure=0.020,
            nb_timepoints=600,
            scan_step=0.310 * 2,  # TTL100
            stage_scan_range=2500,
            vertical_pixels=1024,  # used to calculate the readout time
            offset_view1=1580,
            offset_view2=1720,
            view1_galvo1=4.52,
            view1_galvo2=-4.00,
            view2_galvo1=-4.18,
            view2_galvo2=4.00,
            stripe_reduction_range=0.3,
            stripe_reduction_offset=-0.58
    )
    """Methods are separated into live mode and acquisition mode"""
    # live mode
    # for 561
    # daq_card.select_channel(561)
    daq_card.select_view(1)
    daq_card.select_channel_remove_stripes(488)

    # time lapse mode
    # daq_card.acquire_stacks(channels=[488], view=0)
    # daq_card.acquire_stacks(channels=[561], view=2)
    # daq_card.acquire_stacks(channels=[488, 561], view=0)
