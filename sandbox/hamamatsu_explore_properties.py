import datetime
from copylot.hardware.orca_camera.dcam import Dcamapi, Dcam
from copylot.hardware.orca_camera.dcamapi4 import *

import numpy as np


def dcam_get_properties_name_id_dict(iDevice=0):
    """
    Show supported properties
    """
    name_id_dict = {}
    if Dcamapi.init() is not False:
        dcam = Dcam(iDevice)
        if dcam.dev_open() is not False:
            idprop = dcam.prop_getnextid(0)
            while idprop is not False:
                nameprop = dcam.prop_getname(idprop)
                if nameprop is not False:
                    name_id_dict[nameprop] = idprop

                idprop = dcam.prop_getnextid(idprop)

            dcam.dev_close()
        else:
            print('-NG: Dcam.dev_open() fails with error {}'.format(dcam.lasterr()))
    else:
        print('-NG: Dcamapi.init() fails with error {}'.format(Dcamapi.lasterr()))

    Dcamapi.uninit()
    return name_id_dict


# Initiate Dcamapi:
Dcamapi.init()

# Create the (camera device) Dcam object with the device index
iDevice = 0
dcam = Dcam(iDevice)

# Open the device
dcam.dev_open()

dcam.prop_getvaluetext(idprop=DCAM_IDPROP.OUTPUTTRIGGER_ACTIVE, fValue=1)  # EDGE

dcam.prop_getvaluetext(idprop=DCAM_IDPROP.OUTPUTTRIGGER_KIND, fValue=1)  # LOW
dcam.prop_getvaluetext(idprop=DCAM_IDPROP.OUTPUTTRIGGER_KIND, fValue=2)  # exposure
dcam.prop_getvaluetext(idprop=DCAM_IDPROP.OUTPUTTRIGGER_KIND, fValue=3)  # programmable
dcam.prop_getvaluetext(idprop=DCAM_IDPROP.OUTPUTTRIGGER_KIND, fValue=4)  # trigger ready
dcam.prop_getvaluetext(idprop=DCAM_IDPROP.OUTPUTTRIGGER_KIND, fValue=5)  # high

dcam.prop_getvaluetext(idprop=DCAM_IDPROP.MASTERPULSE_MODE, fValue=1)  # 'CONTINUOUS'
dcam.prop_getvaluetext(idprop=DCAM_IDPROP.MASTERPULSE_MODE, fValue=2)  # 'START'
dcam.prop_getvaluetext(idprop=DCAM_IDPROP.MASTERPULSE_MODE, fValue=3)  # 'BURST'

dcam.prop_getvaluetext(idprop=DCAM_IDPROP.MASTERPULSE_TRIGGERSOURCE, fValue=1)  # 'EXTERNAL'
dcam.prop_getvaluetext(idprop=DCAM_IDPROP.MASTERPULSE_TRIGGERSOURCE, fValue=2)  # 'SOFTWARE'

dcam.prop_getvaluetext(idprop=DCAM_IDPROP.TRIGGER_MODE, fValue=1)  # 'NORMAL'

dcam.prop_getvaluetext(idprop=DCAM_IDPROP.TRIGGERSOURCE, fValue=1)  # 'INTERNAL'
dcam.prop_getvaluetext(idprop=DCAM_IDPROP.TRIGGERSOURCE, fValue=2)  # 'EXTERNAL'
dcam.prop_getvaluetext(idprop=DCAM_IDPROP.TRIGGERSOURCE, fValue=3)  # 'SOFTWARE'
dcam.prop_getvaluetext(idprop=DCAM_IDPROP.TRIGGERSOURCE, fValue=4)  # 'MASTER PULSE'

# trigger times is a configurable property
# dcam.prop_setgetvalue(idprop=DCAM_IDPROP.TRIGGERTIMES, fValue=1)
# Out[6]: 1.0
# dcam.prop_setgetvalue(idprop=DCAM_IDPROP.TRIGGERTIMES, fValue=2)
# Out[7]: 2.0
# dcam.prop_setgetvalue(idprop=DCAM_IDPROP.TRIGGERTIMES, fValue=20)
# Out[8]: 20.0

dcam.prop_getvaluetext(idprop=DCAM_IDPROP.SENSORMODE, fValue=1)  # 'AREA'

dcam.prop_setgetvalue(idprop=DCAM_IDPROP.TRIGGER_MODE, fValue=1)  # 'NORMAL'

dcam.prop_getvaluetext(idprop=DCAM_IDPROP.CAPTUREMODE, fValue=2)
dcam.prop_getvaluetext(idprop=DCAM_IDPROP.OUTPUTTRIGGER_BASESENSOR, fValue=2)
dcam.prop_getvaluetext(idprop=DCAM_IDPROP.OUTPUTTRIGGER_BASESENSOR, fValue=1)

dcam.prop_getvaluetext(idprop=DCAM_IDPROP.TRIGGERPOLARITY, fValue=2)  # positive

dcam.prop_getvaluetext(idprop=DCAM_IDPROP.SENSORMODE, fValue=1)  # 'AREA'

dcam.prop_getvaluetext(idprop=DCAM_IDPROP.COLORTYPE, fValue=1)  # 'B/W' - only this.

dcam.prop_getvaluetext(idprop=DCAM_IDPROP.TRIGGER_CONNECTOR, fValue=2)  # 'BNC'

dcam.prop_getvaluetext(idprop=DCAM_IDPROP.BINNING, fValue=1)  # 1x1
dcam.prop_getvaluetext(idprop=DCAM_IDPROP.BINNING, fValue=2)  # 2x2

# dcam.prop_getvalue(idprop=DCAM_IDPROP.BITSPERCHANNEL)
# Out[4]: 16.0


# read out speed has to be 2.0
# dcam.prop_setgetvalue(idprop=DCAM_IDPROP.READOUTSPEED, fValue=1)
# Out[5]: False
# dcam.prop_setgetvalue(idprop=DCAM_IDPROP.READOUTSPEED, fValue=2)
# Out[6]: 2.0
# dcam.prop_setgetvalue(idprop=DCAM_IDPROP.READOUTSPEED, fValue=3)
# Out[7]: False
# dcam.prop_setgetvalue(idprop=DCAM_IDPROP.READOUTSPEED, fValue=4)
# Out[8]: False

# read out direction has to be 5.0
# dcam.prop_getvalue(idprop=DCAM_IDPROP.READOUT_DIRECTION)
# Out[12]: 5.0
# dcam.prop_setgetvalue(idprop=DCAM_IDPROP.READOUT_DIRECTION, fValue=1)
# Out[13]: False
# dcam.prop_setgetvalue(idprop=DCAM_IDPROP.READOUT_DIRECTION, fValue=5)
# Out[14]: 5.0
# dcam.prop_setgetvalue(idprop=DCAM_IDPROP.READOUT_DIRECTION, fValue=6)
# Out[15]: False
# dcam.prop_setgetvalue(idprop=DCAM_IDPROP.READOUT_DIRECTION, fValue=3)
# Out[16]: False
#

# timing exposure has to be 3.0
# dcam.prop_setgetvalue(idprop=DCAM_IDPROP.TIMING_EXPOSURE, fValue=3)
#   ...:
# Out[6]: 3.0
