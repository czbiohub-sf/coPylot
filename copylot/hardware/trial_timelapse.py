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
nb_view = 1
nb_frames = 1000
step_size_um = 0.310 * 2
range_in_um = 500
interval_in_seconds = 60 * 4

scan_mode = ASIStageScanMode.RASTER  # raster or serpentine
custom_offset_in_um = 0  # offset between two views for better coverage
nr_channels = nb_view

angle = 45
res = 0.439  # xy pixel size

alignment_offset_in_um = 0
galvo_offset_in_um = 0
offset = alignment_offset_in_um + galvo_offset_in_um + custom_offset_in_um

nb_slices = range_in_um / step_size_um
# reset the scanning range for multi channel imaging
# if nb_slices % nb_channel != 0:
#     nb_slices -= nb_slices % nb_channel
#     range_in_um = nb_slices * step_size_um
print(f"nb_slices: {nb_slices}")


exposure_in_ms = 10
print(f"exposure in ms: {exposure_in_ms}")


port = "COM4"
asi_stage = ASIStage(com_port=port)

speed = step_size_um / exposure_in_ms
print(f"scan range in um: {range_in_um}")


save_path = join(path, path_prefix)

axis_order = ["z", "channel", "time", "position"]

asi_stage.set_scan_mode(scan_mode)
asi_stage.set_backlash()


# Set camera for external trigger and validate

# Set camera trigger delay and validate


# Acquisition loop
# for f in range(nb_frames):


# Set camera for internal trigger and validate


asi_stage.set_default_speed()
