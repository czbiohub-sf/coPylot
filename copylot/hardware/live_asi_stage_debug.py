from copylot.hardware.asi_stage.stage import ASIStage, ASIStageScanMode


# Define constants
scan_mode = ASIStageScanMode.RASTER
speed = 0.155 / 2
range_in_um = 250
offset = 300
port = "COM6"

# Create ASIStage instance
asi_stage = ASIStage(com_port=port)

# Initialize the stage and zero it
asi_stage.set_scan_mode(scan_mode)
asi_stage.set_backlash()
asi_stage.set_speed(speed=speed)
asi_stage.zero()

view = 0


for _ in range(300):
    # Set scan range
    if view == 0:
        asi_stage.scanr(x=0, y=range_in_um / 1000)
        asi_stage.scanv(x=0, y=0, f=1.0)
    else:
        asi_stage.scanr(
            x=-offset / 1000, y=(-offset + range_in_um) / 1000
        )
        asi_stage.scanv(x=0, y=0, f=1.0)

    asi_stage.start_scan()

asi_stage.set_default_speed()

