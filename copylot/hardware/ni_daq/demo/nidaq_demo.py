from copylot.hardware.ni_daq.legacy_daxi_nidaq import NIDaq


if __name__ == "__main__":
    daq_card = NIDaq(
        exposure=0.100,
        nb_timepoints=2000,  # number of timepoints
        scan_step=0.155 * 5,  # TTL100, 0.310, TTL300 0.103, TTL200 0.155 0.155 * 2
        scan_range=250,  # starts from current position
        vertical_pixels=2048,  # used to calculate the readout time
        galvo_offset_view1=1600,  # scanning galvo central position for view1
        galvo_offset_view2=1750,  # scanning galvo central position for view2
        o3_view1=40,  # unit: um, offset of O3 (king snouty) needed for view1, focus control
        o3_view2=30,  # unit: um, offset of O3 (king snouty) needed for view2, focus control
        view1_galvo1=3.95,  # position of galvo1 for view 1
        view1_galvo2=-4.2,  # position of galvo2 for view 1
        view2_galvo1=-4.1,  # position of galvo1 for view 2
        view2_galvo2=3.85,  # position of galvo2 for view 2
        stripe_reduction_range=0.5,  # 2-axes galvo, range of gamma control
        stripe_reduction_offset=-0.9,  # 2-axes galvo, offset of gamma control
        o1_pifoc=0,  # position of O1 pifoc, range [-400, 400] um
        light_sheet_angle=-2.72,  # 2-axes galvo, beta control of light sheet angle, -0.22 -> epi
    )
    """Methods are separated into live mode and aacquisition mode"""

    #############
    # live mode
    # view = 1, first view; view = 2, second view; view = 3, both views;
    # channel = ['405'], ['488'], ['561'], ['639'], ['bf'] or anY combination;
    # daq_card.select_view(2)
    # daq_card.select_channel('bf')

    #############
    # time lapse mode
    # view = 1, first view; view = 2, second view; view = 3, both views;
    # channel = ['405'], ['488'], ['561'], ['639'], ['bf'] or anY combination;
    # scanning mode: 'Stage', 'Gavlo', 'O1'

    daq_card.acquire_stacks(
        channels=['488', '561'], view=3, scan_option="Stage", interleave=False
    )
