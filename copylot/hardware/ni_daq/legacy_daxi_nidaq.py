"""making ao channel to send a sequence of signals"""
import nidaqmx
import nidaqmx.system
import numpy as np
import time


def set_dio_state(ch, value):
    """set a DIO channel,
    false to low, true to high"""
    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(ch)
        task.write([value], auto_start=True)


def set_ao_value(ch, value):
    """set the ao channel to value"""
    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan(ch)
        task.write([value], auto_start=True)


class NIDaq:
    """
    NI DAQ card adapter.

    Parameters
    ----------
    exposure : float
        Expose time. Its unit is seconds.
    nb_timepoints : int
        Number of timepoints. Number of stacks to acquire.
    scan_step : float
        Scanning step size. unit: um.
    scan_range : float
        Total range of stage scanning. unit: um.
    vertical_pixels : int
        Number of pixels along the vertical direction, unit: pixels
    num_samples: int
        Number of samples of each channel (AO and DO) during each camera exposure
    galvo_offset_view1: float
        Offset of scanning galvo needed for view1, unit: um
    galvo_offset_view2: float
        Offset of scanning galvo needed for view2, unit: um
    o3_view1 : float
        Offset of O3(objective-3) needed for view1, focus control
    o3_view2 : float
        Offset of O3(objective-3) needed for view2, focus control
    view1_galvo1 : float
        Voltage to apply on galvo 1 for view 1
    view1_galvo2 : float
        Voltage to apply on galvo 2 for view 1
    view2_galvo1 : float
        Voltage to apply on galvo 1 for view 2
    view2_galvo2 : float
        Voltage to apply on galvo 2 for view 2
    stripe_reduction_range : float
        Voltage to apply on galvo gamma to reduce stripe range
    stripe_reduction_offset : float
        Voltage to apply on galvo gamma to reduce stripe offset
    o1_pifoc : int
        Offset of O1(Objective-1) PIFOC in um, range [-400, 400] um.
    light_sheet_angle : float
        Voltage to apply on galvo beta to adjust light sheet angle
    laser_power
        Percentage value in [0, 100], for laser analog control

    """

    # Channel information
    ch_ao0 = "cDAQ1AO/ao0"  # scanning channel
    ch_ao1 = "cDAQ1AO/ao1"  # view switching
    ch_ao2 = "cDAQ1AO/ao2"  # view switching
    ch_ao3 = "cDAQ1AO/ao3"  # gamma angle, stripe reduction
    ch_ao4 = "cDAQ1AO2/ao0"  # beta angle, light sheet incident angle
    ch_ao5 = "cDAQ1AO2/ao1"  # O1 PIFOC control
    ch_ao6 = "cDAQ1AO2/ao2"  # O3 PIFOC control
    ch_ao7 = "cDAQ1AO2/ao3"  # analog control of laser power

    ch_ctr0 = "cDAQ1/_ctr0"  # for retrigger
    ch_ctr0_internal_output = "/cDAQ1/Ctr0InternalOutput"
    ch_ctr1 = "cDAQ1/_ctr1"  # for counting number of frames
    ch_ctr1_internal_output = "/cDAQ1/Ctr1InternalOutput"
    ch_ctr2 = "cDAQ1/_ctr2"  # idle
    ch_ctr3 = "cDAQ1/_ctr3"  # idle

    PFI0 = "/cDAQ1/PFI0"  # camera exposure input
    PFI1 = "/cDAQ1/PFI1"  # idle

    ch_dio0 = "cDAQ1DIO/port0/line0"  # 405 digital channel
    ch_dio1 = "cDAQ1DIO/port0/line1"  # 488 digital channel
    ch_dio2 = "cDAQ1DIO/port0/line2"  # 561 digital channel
    ch_dio3 = "cDAQ1DIO/port0/line3"  # 639 digital channel
    ch_dio4 = "cDAQ1DIO/port0/line4"  # bright field
    ch_dio5 = "cDAQ1DIO/port0/line5"  # idle
    ch_dio6 = "cDAQ1DIO/port0/line6"  # idle
    ch_dio7 = "cDAQ1DIO/port0/line7"  # idle

    NB_DUMMY_TTLS = 2  # the number of dummy TTLs from the Flash4 camera

    # constants
    MAX_VOL = 10  # unit: v, maximum voltage of the ao channels
    MIN_VOL = -10  # unit: v, minimal voltage of the ao channels
    MIN_VOL_O3 = -10  # unit: v, minimal voltage of the PIFOC O3
    MIN_LASER_ANALOG = 0  # unit: v, minimal voltage for laser analog control
    MAX_LASER_ANALOG = 5  # unit: v, maximal voltage for laser analog control
    CONVERT_RATIO_SCAN_GALVO = (
        159  # unit: um / v, to convert from voltage to the scan distance of the galvo
    )
    CONVERT_RATIO_PIFOC_O1 = 40  # unit: um / v, to convert from voltage to the scan distance of the PIFOC O1 [-400, 400]
    CONVERT_RATIO_PIFOC_O3 = 10  # unit: um / v, to convert from voltage to the scan distance of the PIFOC O3 [0, 100]
    READOUT_TIME_FULL_CHIP = (
        0.01  # unit: second, the readout time of the full chip camera
    )
    MAX_VERTICAL_PIXELS = (
        2048  # unit: pixels, maximal number of pixels along the vertical direction
    )

    def __init__(
        self,
        exposure: float,
        nb_timepoints: int,
        scan_step: float,
        scan_range: float,
        *,
        vertical_pixels: int = 2048,  # unit: pixels, number of pixels along the vertical direction
        num_samples: int = 20,  # default value, for timing, only important for scan galvo during stage scan
        galvo_offset_view1: float = 1550,  # unit: um, offset of scanning gavlo needed for view1
        galvo_offset_view2: float = 1650,  # unit: um, offset of scanning gavlo needed for view2
        o3_view1: float = 50,  # unit: um, offset of O3 needed for view1, focus control
        o3_view2: float = 50,  # unit: um, offset of O3 needed for view2, focus control
        view1_galvo1: float = 4.2,  # unit: v, to apply on galvo 1 for view 1
        view1_galvo2: float = -4.08,  # unit: v, to apply on galvo 2 for view 1
        view2_galvo1: float = -4.37,  # unit: v, to apply on galvo 1 for view 2
        view2_galvo2: float = 3.66,  # unit: v, to apply on galvo 2 for view 2
        stripe_reduction_range: float = 0.1,  # unit: v, to apply on galvo gamma to reduce stripe
        stripe_reduction_offset: float = 0.58,  # unit: v, to apply on galvo gamma to reduce stripe
        o1_pifoc: int = 0,  # unit: um, to apply on O1 PIFOC, [-400, 400] um.
        light_sheet_angle: float = -2.2,  # unit: v, to apply on galvo beta to adjust light sheet angle
        laser_power=100,  # unit: percentage [0, 100], for laser analog control
    ):
        self.stop_now = False

        self.exposure = exposure
        self.nb_timepoints = nb_timepoints
        self.scan_step = scan_step
        self.scan_range = scan_range
        self.readout_time = (
            self.READOUT_TIME_FULL_CHIP * vertical_pixels / self.MAX_VERTICAL_PIXELS
        )
        self.num_samples = num_samples
        self.offset_view1 = galvo_offset_view1
        self.offset_view2 = galvo_offset_view2
        self.o3_view1 = o3_view1
        self.o3_view2 = o3_view2
        self.view1_galvo1 = view1_galvo1
        self.view1_galvo2 = view1_galvo2
        self.view2_galvo1 = view2_galvo1
        self.view2_galvo2 = view2_galvo2
        self.stripe_reduction_range = stripe_reduction_range
        self.stripe_reduction_offset = stripe_reduction_offset
        self.o1_pifoc = o1_pifoc
        self.light_sheet_angle = light_sheet_angle
        self.laser_power_percent = laser_power
        print("number of slices:", self.nb_slices)
        print("current sampling_rate is:", self.sampling_rate)

    @property
    def nb_slices(self):
        """Number of slices"""
        return int(self.scan_range / self.scan_step)

    @property
    def sampling_rate(self):
        """Sampling rate"""
        return self.num_samples / self.exposure

    def _get_ao_data(self, view: str, scan_option: str = "Stage"):
        """Generate the ndarray for an ao channel

        Parameters
        ----------
        view : str
        scan_option : str

        Returns
        -------
        TODO: write the return type and description

        """
        # AO3. for stripe reduction
        stripe_min = -self.stripe_reduction_range + self.stripe_reduction_offset
        stripe_max = self.stripe_reduction_range + self.stripe_reduction_offset
        nb_on_sample = round((self.exposure - self.readout_time) * self.sampling_rate)
        nb_off_sample = round(self.readout_time * self.sampling_rate)
        data_ao3 = list(np.linspace(stripe_min, stripe_max, nb_on_sample))
        data_ao3.extend([stripe_min] * nb_off_sample)

        # AO4, for fixed light sheet angle
        data_ao4 = [self.light_sheet_angle] * self.num_samples

        # AO7, for laser analog control
        data_ao7 = [
            self.laser_power_percent / 100 * self.MAX_LASER_ANALOG
        ] * self.num_samples

        # AO1, AO2 and AO6, for view switching and light sheet stabilization
        if view == "view1":
            offset = self._offset_distance_to_voltage(
                self.offset_view1
            )  # convert the offset from um to v
            data_ao1 = [self.view1_galvo1] * self.num_samples
            data_ao2 = [self.view1_galvo2] * self.num_samples
            data_ao6 = [self.o3_view1 / self.CONVERT_RATIO_PIFOC_O3] * self.num_samples
        elif view == "view2":
            offset = self._offset_distance_to_voltage(
                self.offset_view2
            )  # convert the offset from um to v
            data_ao1 = [self.view2_galvo1] * self.num_samples
            data_ao2 = [self.view2_galvo2] * self.num_samples
            data_ao6 = [self.o3_view2 / self.CONVERT_RATIO_PIFOC_O3] * self.num_samples

        # AO0 and AO5 depends in scanning option
        if scan_option == "Stage":
            # AO0, stablize light sheet during stage scanning
            min_range = -self.scan_step / 2 / self.CONVERT_RATIO_SCAN_GALVO
            max_range = self.scan_step / 2 / self.CONVERT_RATIO_SCAN_GALVO
            # v change scan for stablizing galvo
            data_ao0_on = list(
                np.linspace(max_range + offset, min_range + offset, self.num_samples)
            )
            data_ao0_off = list(
                np.linspace(
                    data_ao0_on[nb_on_sample], max_range + offset, nb_off_sample
                )
            )
            data_ao0 = data_ao0_on[:nb_on_sample] + data_ao0_off

            # AO5, for fixed O1 position
            data_ao5 = [self.o1_pifoc / self.CONVERT_RATIO_PIFOC_O1] * self.num_samples

        return [
            data_ao0,
            data_ao1,
            data_ao2,
            data_ao3,
            data_ao4,
            data_ao5,
            data_ao6,
            data_ao7,
        ]

    def _get_do_data(self, nb_channels, interleave=False, current_ch=0):
        """Method to get digital output data.

        Parameters
        ----------
        nb_channels
        interleave
        current_ch

        Returns
        -------
        list

        """
        nb_on_sample = round((self.exposure - self.readout_time) * self.sampling_rate)
        data_on = [True] * nb_on_sample + [False] * (self.num_samples - nb_on_sample)
        data_off = [False] * self.num_samples

        if nb_channels == 1:
            return data_on
        else:
            data = []
            # only generate data once if interleaved channel acquisition
            if interleave:
                for i in range(nb_channels):
                    data.append(
                        data_off * i + data_on + data_off * (nb_channels - i - 1)
                    )
            # generate data for each channel for sequential channel acquisition
            else:
                for ch in range(nb_channels):
                    if ch == current_ch:
                        data.append(data_on)
                    else:
                        data.append(data_off)
            return data

    def _crate_ao_task_for_acquisition(self):
        """create ao task for acquisition, include all the needed ao channels"""
        task_ao = nidaqmx.Task("ao0")
        task_ao.ao_channels.add_ao_voltage_chan(self.ch_ao0)
        task_ao.ao_channels.add_ao_voltage_chan(self.ch_ao1)
        task_ao.ao_channels.add_ao_voltage_chan(self.ch_ao2)
        task_ao.ao_channels.add_ao_voltage_chan(self.ch_ao3)
        task_ao.ao_channels.add_ao_voltage_chan(self.ch_ao4)
        task_ao.ao_channels.add_ao_voltage_chan(self.ch_ao5)
        task_ao.ao_channels.add_ao_voltage_chan(self.ch_ao6)
        task_ao.ao_channels.add_ao_voltage_chan(self.ch_ao7)
        return task_ao

    def _crate_do_task_for_acquisition(self, channels):
        """Create ao task for acquisition, include all the needed ao channels

        Parameters
        ----------
        channels : Sequence[str]

        Returns
        -------
        nidaqmx.Task

        """
        task_do = nidaqmx.Task("do0")  # for laser control

        # select channel
        for ch in channels:
            if ch == '405':
                task_do.do_channels.add_do_chan(self.ch_dio0)
            elif ch == '488':
                task_do.do_channels.add_do_chan(self.ch_dio1)
            elif ch == '561':
                task_do.do_channels.add_do_chan(self.ch_dio2)
            elif ch == '639':
                task_do.do_channels.add_do_chan(self.ch_dio3)
            elif ch == 'bf':
                task_do.do_channels.add_do_chan(self.ch_dio4)
            else:
                raise ValueError("Channel not supported")
        return task_do

    def acquire_stacks(
        self,
        channels,
        view,
        scan_option='Stage',
        interleave=True,
    ):
        """Acquire stackes, depending on the given channel and view.

        Parameters
        ----------
        channels : List[str]
            ['405'], ['488'], ['561'], ['639'], ['bf'] or any combination of them
        view : int
            view=1 first view only, view=2 second view only, view=3 both views
        scan_option : str
            valid values are 'Stage', 'O1, 'Galvo'
        interleave : bool

        """
        # If using interleave mode
        # for multichannel acquistion, make sure each channel has the same number of slices
        if interleave:
            if len(channels) > 1 and self.nb_slices % len(channels) != 0:
                nb_slices = self.nb_slices - self.nb_slices % len(channels)
                self.scan_range = nb_slices * self.scan_step

        # use different acquisition methods for each scanning option
        if scan_option == 'Stage':
            fn_acquire = self._acquire_stacks
        elif scan_option == 'O1' or 'Galvo':
            # set the initial states of the AO devices before acquisition
            self.set_initial_states(scan_option, view)
            fn_acquire = self._acquire_stacks_galvo
        # elif scan_option == 'Interleave_denoising':
        #     fn_acquire = self._acquire_stacks_interleave_denoising
        else:
            raise ValueError("Scanning mode not supported")
        task_ao = self._crate_ao_task_for_acquisition()
        task_do = self._crate_do_task_for_acquisition(channels)

        # select view
        nr_channels = len(channels)
        if view == 1:
            # if scan_option == 'Interleave_denoising':
            #     fn_acquire(task_ao, task_do, nr_channels, ['view1'], scan_option, interleave, low_power, high_power)
            # else:
            fn_acquire(
                task_ao, task_do, nr_channels, ['view1'], scan_option, interleave
            )
        elif view == 2:
            # if scan_option == 'Interleave_denoising':
            #     fn_acquire(task_ao, task_do, nr_channels, ['view2'], scan_option, interleave, low_power, high_power)
            # else:
            fn_acquire(
                task_ao, task_do, nr_channels, ['view2'], scan_option, interleave
            )
        elif view == 3:
            # if scan_option == 'Interleave_denoising':
            #     fn_acquire(task_ao, task_do, nr_channels, ['view1', 'view2'], scan_option, interleave,
            #                low_power, high_power)
            # else:
            fn_acquire(
                task_ao,
                task_do,
                nr_channels,
                ['view1', 'view2'],
                scan_option,
                interleave,
            )
        else:
            raise ValueError("View not supported")

        task_ao.close()
        task_do.close()

    def _acquire_stacks(
        self, task_ao, task_do, nr_channels, views, scan_option, interleave
    ):
        """
        Set up the workflow to acquire multiple stacks

        Parameters
        ----------
        task_ao
        task_do
        nr_channels
        views
        scan_option
        interleave

        """

        data_ao = [
            self._get_ao_data(v, scan_option) for v in views
        ]  # different for each view due to different offsets

        data_do = self._get_do_data(
            nr_channels, interleave
        )  # get the digital output data depending on the channels

        # set up the counter for count the slices for a zstack
        task_ctr_loop = nidaqmx.Task("counter0")
        ctr_loop = task_ctr_loop.ci_channels.add_ci_count_edges_chan(
            self.ch_ctr1, edge=nidaqmx.constants.Edge.RISING
        )
        ctr_loop.ci_count_edges_term = self.PFI0

        # set up the counter to retrigger the ao and do channels
        task_ctr_retrig = nidaqmx.Task("counter1")
        task_ctr_retrig.co_channels.add_co_pulse_chan_freq(
            self.ch_ctr0,
            idle_state=nidaqmx.constants.Level.LOW,
            freq=self.sampling_rate,
        )
        task_ctr_retrig.timing.cfg_implicit_timing(
            sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
            samps_per_chan=self.num_samples,
        )
        task_ctr_retrig.triggers.start_trigger.cfg_dig_edge_start_trig(
            trigger_source=self.PFI0, trigger_edge=nidaqmx.constants.Slope.RISING
        )
        task_ctr_retrig.triggers.start_trigger.retriggerable = True

        # set up ao channel
        task_ao.timing.cfg_samp_clk_timing(
            rate=self.sampling_rate,
            source=self.ch_ctr0_internal_output,
            sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
        )

        # set up the do channel
        task_do.timing.cfg_samp_clk_timing(
            rate=self.sampling_rate,
            source=self.ch_ctr0_internal_output,
            sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
        )

        task_ctr_retrig.start()
        for _ in range(self.nb_timepoints):
            for v in range(len(data_ao)):  # change view
                task_ao.write(data_ao[v])
                task_ao.start()
                print("number of slices to acquire:", self.nb_slices)
                for ch in range(nr_channels):
                    # regenerate do date for non-interleaved multichannel acquisition
                    if not interleave and nr_channels > 1:
                        data_do = self._get_do_data(
                            nr_channels, interleave, current_ch=ch
                        )

                    task_do.write(data_do)
                    task_do.start()

                    task_ctr_loop.start()
                    counts = 0
                    while (
                        counts < self.nb_slices + 1
                    ):  # Flash4.0 outputs 1 more pulse than asked
                        counts = task_ctr_loop.read()
                        time.sleep(0.005)  # wait time during loop
                    task_ctr_loop.stop()
                    print("counts: ", counts)
                    # print("counts: ", counts)
                    time.sleep(
                        self.exposure + 0.1
                    )  # add time to allow ao and do output for the last frame
                    task_do.stop()
                    print("one stack done!")
                task_ao.stop()

        # task_ctr_retrig.stop()
        task_ctr_retrig.close()
        task_ctr_loop.close()

    def _get_ao_data_galvo(self, view: str, scan_option="O1"):
        """Generate the ndarray for an ao channel

        Parameters
        ----------
        view : str
        scan_option : str

        Returns
        -------
        TODO: fill the correct return type and description

        """
        nb_samples = self.NB_DUMMY_TTLS + self.nb_slices
        # AO3. not stripe reduction in this mode
        data_ao3 = [self.stripe_reduction_offset] * nb_samples

        # AO4, for fixed light sheet angle
        data_ao4 = [self.light_sheet_angle] * nb_samples

        # AO1 and AO2, for view switching and light sheet stabilization
        if view == "view1":
            offset = self._offset_distance_to_voltage(
                self.offset_view1
            )  # convert the offset from um to v
            data_ao1 = [self.view1_galvo1] * nb_samples
            data_ao2 = [self.view1_galvo2] * nb_samples
            data_ao6 = [self.o3_view2 / self.CONVERT_RATIO_PIFOC_O3] * nb_samples
        elif view == "view2":
            offset = self._offset_distance_to_voltage(
                self.offset_view2
            )  # convert the offset from um to v
            data_ao1 = [self.view2_galvo1] * nb_samples
            data_ao2 = [self.view2_galvo2] * nb_samples
            data_ao6 = [self.o3_view2 / self.CONVERT_RATIO_PIFOC_O3] * nb_samples

        # AO0 and AO5 depends in scanning option
        if scan_option == "O1":
            # AO0, for fixed scan galvo position
            data_ao0 = [offset] * nb_samples
            # AO5, for O1  scanning
            min_range = (
                self.o1_pifoc - self.scan_range / 2
            ) / self.CONVERT_RATIO_PIFOC_O1
            step = self.scan_step / self.CONVERT_RATIO_PIFOC_O1
            data_ao5 = [x * step + min_range for x in range(nb_samples)]
        elif scan_option == "Galvo":
            # for fixed O1 position
            data_ao5 = [self.o1_pifoc / self.CONVERT_RATIO_PIFOC_O1] * nb_samples
            # for scan galvo ramp
            min_range = offset - self.scan_range / 2 / self.CONVERT_RATIO_SCAN_GALVO
            step = self.scan_step / self.CONVERT_RATIO_SCAN_GALVO
            data_ao0 = [x * step + min_range for x in range(nb_samples)]

        return [data_ao0, data_ao1, data_ao2, data_ao3, data_ao4, data_ao5, data_ao6]

    def _acquire_stacks_galvo(self, task_ao, task_do, channels, views, scan_option):
        """Set up the workflow to acquire multiple stacks
        todo, support multichannel imaging

        Parameters
        ----------
        task_ao
        task_do
        channels
        views
        scan_option

        """
        data_ao = [
            self._get_ao_data_galvo(v, scan_option) for v in views
        ]  # different for each view due to different offsets

        data_do = self._get_do_data(
            channels
        )  # get the digital output data depending on the channels

        # set up the counter for loop through a zstack
        task_ctr_loop = nidaqmx.Task("counter0")
        ctr_loop = task_ctr_loop.ci_channels.add_ci_count_edges_chan(
            self.ch_ctr1, edge=nidaqmx.constants.Edge.RISING
        )
        ctr_loop.ci_count_edges_term = self.PFI0

        # set up the counter to retrigger the do channels
        task_ctr_retrig = nidaqmx.Task("counter1")
        task_ctr_retrig.co_channels.add_co_pulse_chan_freq(
            self.ch_ctr0,
            idle_state=nidaqmx.constants.Level.LOW,
            freq=self.sampling_rate,
        )
        task_ctr_retrig.timing.cfg_implicit_timing(
            sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
            samps_per_chan=self.num_samples,
        )
        task_ctr_retrig.triggers.start_trigger.cfg_dig_edge_start_trig(
            trigger_source=self.PFI0, trigger_edge=nidaqmx.constants.Slope.RISING
        )
        task_ctr_retrig.triggers.start_trigger.retriggerable = True

        # set up ao channel
        nb_samples = self.NB_DUMMY_TTLS + self.nb_slices
        task_ao.timing.cfg_samp_clk_timing(
            rate=nb_samples,
            samps_per_chan=nb_samples,
            source=self.PFI1,
            sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
            active_edge=nidaqmx.constants.Slope.FALLING,
        )

        task_ao.triggers.start_trigger.cfg_dig_edge_start_trig(
            trigger_source=self.PFI0, trigger_edge=nidaqmx.constants.Slope.RISING
        )

        task_ctr_retrig.start()
        for _ in range(self.nb_timepoints):
            for v in range(len(data_ao)):  # change view
                task_ao.write(data_ao[v])
                task_ao.start()
                for i_ch in range(
                    1
                ):  # interleaved acquisition, todo support also sequential channel imaging
                    # set up the do channel
                    task_do.timing.cfg_samp_clk_timing(
                        rate=self.sampling_rate,
                        source=self.ch_ctr0_internal_output,
                        sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
                    )
                    task_do.write(data_do)
                    task_do.start()

                    task_ctr_loop.start()
                    counts = 0
                    while (
                        counts < self.nb_slices + 1
                    ):  # Flash4.0 outputs 1 more pulse than asked
                        counts = task_ctr_loop.read()
                        time.sleep(0.005)  # wait time during loop
                    task_ctr_loop.stop()
                    print("counts: ", counts)
                    # print("counts: ", counts)
                    time.sleep(
                        self.exposure + 0.1
                    )  # add time to allow ao and do output for the last frame
                    task_do.stop()
                    print("one stack done!")
                task_ao.stop()

        # task_ctr_retrig.stop()
        task_ctr_retrig.close()
        task_ctr_loop.close()

    def _acquire_stacks_interleave_denoising(
        self,
        task_ao,
        task_do,
        nr_channels,
        views,
        scan_option,
        interleave,
    ):
        """Set up the workflow to acquire multiple stacks,
        for interleaved denoising purpose only

        Parameters
        ----------
        task_ao
        task_do
        nr_channels
        views
        scan_option
        interleave

        """
        data_ao = [
            self._get_ao_data(v, scan_option) for v in views
        ]  # different for each view due to different offsets

        data_do = self._get_do_data(
            nr_channels, interleave
        )  # get the digital output data depending on the channels

        # set up the counter for loop through a zstack
        task_ctr_loop = nidaqmx.Task("counter0")
        ctr_loop = task_ctr_loop.ci_channels.add_ci_count_edges_chan(
            self.ch_ctr1, edge=nidaqmx.constants.Edge.RISING
        )
        ctr_loop.ci_count_edges_term = self.PFI0

        # set up the counter to retrigger the ao and do channels
        task_ctr_retrig = nidaqmx.Task("counter1")
        task_ctr_retrig.co_channels.add_co_pulse_chan_freq(
            self.ch_ctr0,
            idle_state=nidaqmx.constants.Level.LOW,
            freq=self.sampling_rate,
        )
        task_ctr_retrig.timing.cfg_implicit_timing(
            sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
            samps_per_chan=self.num_samples,
        )
        task_ctr_retrig.triggers.start_trigger.cfg_dig_edge_start_trig(
            trigger_source=self.PFI0, trigger_edge=nidaqmx.constants.Slope.RISING
        )
        task_ctr_retrig.triggers.start_trigger.retriggerable = True

        # set up ao channel
        task_ao.timing.cfg_samp_clk_timing(
            rate=self.sampling_rate,
            source=self.ch_ctr0_internal_output,
            sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
        )

        # set up the do channel
        task_do.timing.cfg_samp_clk_timing(
            rate=self.sampling_rate,
            source=self.ch_ctr0_internal_output,
            sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
        )

        task_ctr_retrig.start()
        for _ in range(self.nb_timepoints):
            for v in range(len(data_ao)):  # change view
                task_ao.write(data_ao[v])
                task_ao.start()
                print("number of slices to acquire:", self.nb_slices)
                for ch in range(nr_channels):
                    # regenerate do date for non-interleaved multichannel acquisition
                    if not interleave and nr_channels > 1:
                        data_do = self._get_do_data(
                            nr_channels, interleave, current_ch=ch
                        )

                    task_do.write(data_do)
                    task_do.start()

                    task_ctr_loop.start()
                    counts = 0
                    while (
                        counts < self.nb_slices + 1
                    ):  # Flash4.0 outputs 1 more pulse than asked
                        counts = task_ctr_loop.read()
                        time.sleep(0.005)  # wait time during loop
                    task_ctr_loop.stop()
                    print("counts: ", counts)
                    # print("counts: ", counts)
                    time.sleep(
                        self.exposure + 0.1
                    )  # add time to allow ao and do output for the last frame
                    task_do.stop()
                    print("one stack done!")
                task_ao.stop()

        # task_ctr_retrig.stop()
        task_ctr_retrig.close()
        task_ctr_loop.close()

    def _set_initial_ao_states(
        self, scan_galvo, galvo1, galvo2, angle_galvo, o1, o3, laser_power
    ):
        """Select the initial states for the AO channels, by using the correct
        offset of the scanning galvo and the voltages of the switching galvos

        Parameters
        ----------
        scan_galvo
        galvo1
        galvo2
        angle_galvo
        o1
        o3
        laser_power

        """
        data = [scan_galvo, galvo1, galvo2, angle_galvo, o1, o3, laser_power]
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan(self.ch_ao0)
            task.ao_channels.add_ao_voltage_chan(self.ch_ao1)
            task.ao_channels.add_ao_voltage_chan(self.ch_ao2)
            task.ao_channels.add_ao_voltage_chan(self.ch_ao4)
            task.ao_channels.add_ao_voltage_chan(self.ch_ao5)
            task.ao_channels.add_ao_voltage_chan(self.ch_ao6)
            task.ao_channels.add_ao_voltage_chan(self.ch_ao7)
            task.write(data, auto_start=True)

    def select_view(self, view):
        """Select one view in live mode

        TODO: why?
        Note: ao3 is not included here,
        it's with the select_channel function

        Parameters
        ----------
        view : int

        """
        if view == 1:
            self._set_initial_ao_states(
                self._offset_distance_to_voltage(self.offset_view1),
                self.view1_galvo1,
                self.view1_galvo2,
                self.light_sheet_angle,
                self.o1_pifoc / self.CONVERT_RATIO_PIFOC_O1,
                self.o3_view1 / self.CONVERT_RATIO_PIFOC_O3,
                self.laser_power_percent / 100 * self.MAX_LASER_ANALOG,
            )
        elif view == 2:
            self._set_initial_ao_states(
                self._offset_distance_to_voltage(self.offset_view2),
                self.view2_galvo1,
                self.view2_galvo2,
                self.light_sheet_angle,
                self.o1_pifoc / self.CONVERT_RATIO_PIFOC_O1,
                self.o3_view2 / self.CONVERT_RATIO_PIFOC_O3,
                self.laser_power_percent / 100 * self.MAX_LASER_ANALOG,
            )
        else:
            raise ValueError("View not supported")

    def set_initial_states(self, scan_option, view):
        """Set the initial states of the AO channels during acquistion

        Parameters
        ----------
        scan_option : str
        view : int

        """
        if view == 1:
            offset = self.offset_view1
            galvo1 = self.view1_galvo1
            galvo2 = self.view1_galvo2
            o3 = self.o3_view1 / self.CONVERT_RATIO_PIFOC_O3
        elif view == 2:
            offset = self.offset_view2
            galvo1 = self.view2_galvo1
            galvo2 = self.view2_galvo2
            o3 = self.o3_view2 / self.CONVERT_RATIO_PIFOC_O3

        if scan_option == 'O1':
            self._set_initial_ao_states(
                self._offset_distance_to_voltage(offset),
                galvo1,
                galvo2,
                self.light_sheet_angle,
                (self.o1_pifoc - self.scan_range / 2) / self.CONVERT_RATIO_PIFOC_O1,
                o3,
                self.laser_power_percent / 100 * self.MAX_LASER_ANALOG,
            )
        elif scan_option == 'Galvo':
            self._set_initial_ao_states(
                self._offset_distance_to_voltage(offset - self.scan_range / 2),
                galvo1,
                galvo2,
                self.light_sheet_angle,
                self.o1_pifoc / self.CONVERT_RATIO_PIFOC_O1,
                o3,
                self.laser_power_percent / 100 * self.MAX_LASER_ANALOG,
            )
        else:
            raise ValueError("Scanning mode not supported")

    def _offset_distance_to_voltage(self, offset: float) -> float:
        """Convert the offset of each view from um to voltage

        Parameters
        ----------
        offset : float
            unit in um

        Returns
        -------
        float
            unit in V

        """
        return offset / self.CONVERT_RATIO_SCAN_GALVO - self.MAX_VOL

    def _select_channel(self, ch, t=None):
        """Set up DIO channel and Gamma AO channel. Now always do
        remove shadow. Set gamma AO range to 0 if no need for shadow
        removal.

        Parameters
        ----------
        ch
        t

        """
        nb_on_sample = round((self.exposure - self.readout_time) * self.sampling_rate)
        # nb_off_sample = round(self.readout_time * self.sampling_rate)
        data_do = [True] * nb_on_sample + [False] * (self.num_samples - nb_on_sample)

        task_do = nidaqmx.Task()
        task_do.do_channels.add_do_chan(ch)

        task_ao = nidaqmx.Task("ao0")
        task_ao.ao_channels.add_ao_voltage_chan(self.ch_ao3)
        # for stripe reduction
        stripe_min = -self.stripe_reduction_range + self.stripe_reduction_offset
        stripe_max = self.stripe_reduction_range + self.stripe_reduction_offset
        nb_on_sample = round((self.exposure - self.readout_time) * self.sampling_rate)
        nb_off_sample = round(self.readout_time * self.sampling_rate)
        data_ao3 = list(np.linspace(stripe_min, stripe_max, nb_on_sample))
        data_ao3.extend([stripe_min] * nb_off_sample)

        self._retriggable_task(task_do, data_do, task_ao, data_ao3, t)
        set_dio_state(ch, False)

    def select_channel(self, ch, t=None):
        """Select one channel in live mode

        Parameters
        ----------
        ch
        t

        """
        if ch == '405':
            self._select_channel(self.ch_dio0, t)
        elif ch == '488':
            self._select_channel(self.ch_dio1, t)
        elif ch == '561':
            self._select_channel(self.ch_dio2, t)
        elif ch == '639':
            self._select_channel(self.ch_dio3, t)
        elif ch == 'bf':
            self._select_channel(self.ch_dio4, t)
        else:
            raise ValueError("Channel not supported!")

    def _set_up_retriggerable_counter(self, counter):
        """Set up a retriggerable counter task

        Parameters
        ----------
        counter

        Returns
        -------
        nidaqmx.Task

        """
        task_ctr = nidaqmx.Task()
        task_ctr.co_channels.add_co_pulse_chan_freq(
            counter, idle_state=nidaqmx.constants.Level.LOW, freq=self.sampling_rate
        )
        task_ctr.timing.cfg_implicit_timing(
            sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
            samps_per_chan=self.num_samples,
        )
        task_ctr.triggers.start_trigger.cfg_dig_edge_start_trig(
            trigger_source=self.PFI0, trigger_edge=nidaqmx.constants.Slope.RISING
        )
        task_ctr.triggers.start_trigger.retriggerable = True
        return task_ctr

    def _retriggable_task(self, task_do, data_do, task_ao, data_ao, timeout=None):
        """Set up a retriggeable task using a counter
        Using counter0 as default

        Parameters
        ----------
        task_do
        data_do
        task_ao
        data_ao
        timeout

        """
        task_do.timing.cfg_samp_clk_timing(
            rate=self.sampling_rate,
            source=self.ch_ctr0_internal_output,
            sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
        )
        task_ao.timing.cfg_samp_clk_timing(
            rate=self.sampling_rate,
            source=self.ch_ctr0_internal_output,
            sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
        )

        task_ctr = self._set_up_retriggerable_counter(self.ch_ctr0)

        task_do.write(data_do)
        task_ao.write(data_ao)
        task_do.start()
        task_ao.start()
        task_ctr.start()
        print("type s to abort:")
        if timeout is None:
            while input() != "s":
                time.sleep(0.05)
        else:
            time.sleep(timeout)

        task_do.stop()
        task_ao.stop()
        task_ctr.stop()
        task_ctr.close()
        task_do.close()
        task_ao.close()
