"""
This is a script to run basic timelapse together with the
nidaq script. This script tries to mimic the behavior given
in the stageScan_multiPos.bsh script.
"""
import time
from os.path import join
import tensorstore as ts

from copylot.hardware.asi_stage.stage import ASIStage, ASIStageScanMode
from copylot.hardware.hamamatsu_camera.dcam import Dcamapi, Dcam, DCAM_IDPROP, DCAMPROP

path = "D:/data/20210506_xiang"
path_prefix = "stage_TL100_range500um_step0.31_4um_30ms_view2_interval_2s_488_20mW_561_10mW_1800tp_3pos"

nb_channel = 1
nb_view = 2
channels = ["488"]
interleave = False

nb_frames = 1  # number of timepoint
step_size_um = 0.155 * 5
range_in_um = 5
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

nb_slices = int(range_in_um // step_size_um)
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


def main():
    dataset = ts.open(
        {
            "driver": "zarr",
            'kvstore': {
                'driver': 'file',
                'path': r'C:\Users\PiscesScope\Documents\acs\coPylot\test_zarr',
            },
            "key_encoding": ".",
            "metadata": {
                "shape": [nb_slices, nb_view, nb_frames, 2048, 2048],
                "chunks": [128, 1, 128, 128, 128],
                "dtype": "<i2",
                "order": "C",
                "compressor": {
                    "id": "blosc",
                    "shuffle": -1,
                    "clevel": 5,
                    "cname": "lz4",
                },
            },
            'create': True,
            'delete_existing': True,
        }
    ).result()

    write_futures = [None] * int(nb_slices * nb_view * nb_frames)

    asi_stage.set_scan_mode(scan_mode)
    asi_stage.set_backlash()
    asi_stage.set_speed(speed=speed)
    asi_stage.zero()

    if Dcamapi.init():
        dcam = Dcam(0)
        if dcam.dev_open():

            # Set camera for external trigger and validate
            dcam.prop_setvalue(
                DCAM_IDPROP.TRIGGER_MODE, DCAMPROP.TRIGGER_MODE.NORMAL
            )
            dcam.prop_setvalue(
                DCAM_IDPROP.TRIGGERPOLARITY, DCAMPROP.TRIGGERPOLARITY.POSITIVE
            )
            dcam.prop_setvalue(
                DCAM_IDPROP.TRIGGER_CONNECTOR, DCAMPROP.TRIGGER_CONNECTOR.BNC
            )
            dcam.prop_setvalue(
                DCAM_IDPROP.TRIGGERTIMES, 1
            )
            dcam.prop_setvalue(
                DCAM_IDPROP.TRIGGERDELAY, 0
            )


            dcam.prop_setvalue(
                DCAM_IDPROP.TRIGGERSOURCE, DCAMPROP.TRIGGERSOURCE.EXTERNAL
            )
            dcam.prop_setvalue(
                DCAM_IDPROP.TRIGGERACTIVE, DCAMPROP.TRIGGERACTIVE.SYNCREADOUT
            )

            # Set camera trigger delay and validate
            dcam.prop_setvalue(DCAM_IDPROP.TRIGGERDELAY, 0.0)

            if dcam.buf_alloc(3):
                start_time = time.time()

                # Acquisition loop
                for f in range(nb_frames):
                    for view in range(nb_view):

                        if view == 0:
                            asi_stage.scanr(x=0, y=range_in_um / 1000)
                            asi_stage.scanv(x=0, y=0, f=1.0)
                        else:
                            asi_stage.scanr(
                                x=-offset / 1000, y=(-offset + range_in_um) / 1000
                            )
                            asi_stage.scanv(x=0, y=0, f=1.0)
                        print(f"scan range in um: {range_in_um}")

                        # if interleave:
                        print(f"start interleaved acquisition: {interleave}")

                        counter = 0
                        slice = 0
                        timeout_milisec = 1000
                        fps_calculation_interval = 1

                        while slice < nb_slices:
                            asi_stage.start_scan()
                            dcam.cap_start()

                            if dcam.wait_capevent_frameready(timeout_milisec):
                                data = dcam.buf_getlastframedata()
                                print(data.shape)

                                # Async write
                                # write_futures[
                                #     f * (nb_slices * nb_view) + view * nb_slices + slice
                                # ] = dataset[slice, view, f, :, :].write(data)

                            else:
                                dcamerr = dcam.lasterr()
                                if dcamerr.is_timeout():
                                    print('===: timeout')
                                else:
                                    print(
                                        '-NG: Dcam.wait_event() fails with error {}'.format(
                                            dcamerr
                                        )
                                    )
                                    break

                            print(dcam.cap_status())
                            print(dcam.cap_transferinfo().nNewestFrameIndex, dcam.cap_transferinfo().nFrameCount)

                            slice += 1
                            counter += 1

                            if (time.time() - start_time) > fps_calculation_interval:
                                print("FPS: ", counter / (time.time() - start_time))
                                counter = 0
                                start_time = time.time()

                for f in range(nb_frames):
                    for view in range(nb_view):
                        for slice in range(nb_slices):
                            write_futures[
                                f * (nb_slices * nb_view) + view * nb_slices + slice
                            ].result()

                # Set camera for internal trigger and validate
                dcam.prop_setvalue(
                    DCAM_IDPROP.TRIGGERSOURCE, DCAMPROP.TRIGGERSOURCE.INTERNAL
                )

            else:
                print(
                    '-NG: Dcam.buf_alloc(3) fails with error {}'.format(dcam.lasterr())
                )
            dcam.dev_close()

        else:
            print('-NG: Dcam.dev_open() fails with error {}'.format(dcam.lasterr()))

    else:
        print(f"Dcamapi.init() fails with error {Dcamapi.lasterr()}")

    Dcamapi.uninit()

    asi_stage.set_default_speed()


if __name__ == '__main__':
    main()
