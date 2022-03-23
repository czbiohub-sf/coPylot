"""
This is a script to run basic timelapse together with the
nidaq script. This script tries to mimic the behavior given
in the stageScan_multiPos.bsh script.
"""
from os.path import join

from copylot.hardware.asi_stage.stage import ASIStage, ASIStageScanMode

path = "D:/data/20210506_xiang"
path_prefix = "stage_TL100_range500um_step0.31_4um_30ms_view2_interval_2s_488_20mW_561_10mW_1800tp_3pos"

nb_channel = 2
nb_view = 2
channels = ["488", "561"]
interleave = False

nb_frames = 1  # number of timepoint
step_size_um = 0.155 * 5
range_in_um = 250
interval_timepoint_in_seconds = 0
interval_in_seconds = 2

scan_mode = ASIStageScanMode.RASTER  # raster or serpentine
custom_offset_in_um = 300  # offset between two views for better coverage
# nr_channels = nb_view

if nb_channel == 1:
    interleave = True

if not interleave and len(channels) != nb_channel:
    print("number of channels is not consistent")
    nb_channel = len(channels)

angle = 45
res = 0.219  # xy pixel size, TTL100 0.439, TTL200 0.219, TTL300 0.146, TTL165 0.266

alignment_offset_in_um = 0
galvo_offset_in_um = 0
offset = alignment_offset_in_um + galvo_offset_in_um + custom_offset_in_um

nb_slices = range_in_um / step_size_um
# reset the scanning range for multi channel imaging
if nb_slices % nb_channel != 0 and interleave:
    nb_slices -= nb_slices % nb_channel
    range_in_um = nb_slices * step_size_um
print(f"nb_slices: {nb_slices}")


exposure_in_ms = 10
print(f"exposure in ms: {exposure_in_ms}")


port = "COM6"
asi_stage = ASIStage(com_port=port)

speed = step_size_um / exposure_in_ms
print(f"scan range in um: {range_in_um}")


save_path = join(path, path_prefix)

axis_order = ["z", "channel", "time", "position"]

asi_stage.set_scan_mode(scan_mode)
asi_stage.set_backlash()
asi_stage.set_speed(speed=speed)
asi_stage.zero()


# Set camera for external trigger and validate

# Set camera trigger delay and validate


# Acquisition loop
for f in range(nb_frames):
    for view in range(nb_view):

        if view == 0:
            asi_stage.scanr(x=0, y=range_in_um / 1000)
            asi_stage.scanv(x=0, y=0, f=1.0)
        else:
            asi_stage.scanr(x=-offset / 1000, y=(-offset + range_in_um) / 1000)
            asi_stage.scanv(x=0, y=0, f=1.0)
        print(f"scan range in um: {range_in_um}")

        if interleave:
            print(f"start interleaved acquisition: {interleave}")
            asi_stage.start_scan()

            slice = 0


# Set camera for internal trigger and validate


asi_stage.set_default_speed()
