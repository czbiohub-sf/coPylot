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



# initiate Dcamapi:
Dcamapi.init()

# create the (camera device) Dcam object with the device index
iDevice = 0
dcam = Dcam(iDevice)

# open the deivce
dcam.dev_open()

dcam.is_opened()
# allocate buffer
dcam.buf_alloc(3)

# -- try to set exposure time # todo - need to verify if this is working. and think about the order.
v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.EXPOSURETIME,
                          fValue=1)  # The unit here seems to be in seconds.
# -- set external trigger
v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.TRIGGERSOURCE,
                          fValue=2)  # fValue = 2 sets the trigger source to be External Trigger.

v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.TRIGGER_MODE,
                          fValue=1)  # fValue = 1 sets the trigger mode to be 'NORMAL'.

v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.TRIGGERPOLARITY,
                          fValue=2)  # fValue = 2 sets the trigger polarity to be 'POSITIVE'.

v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.TRIGGERTIMES,
                          fValue=1)  # fValue = 1 sets the trigger times to be 10... find out what it means.


v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.OUTPUTTRIGGER_KIND,
                          fValue=2)  # fValue = 2 sets the output trigger kind to be exposure

v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.OUTPUTTRIGGER_POLARITY,
                          fValue=2)  # fValue = 2 sets the trigger polarity to be 'POSITIVE'


v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.OUTPUTTRIGGER_BASESENSOR,
                          fValue=1)  # fValue = 1 sets the output trigger sensor to be 'VIEW 1'.




# # -- choose master pulse burst mode
# v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.MASTERPULSE_MODE,
#                           fValue=3)  # fValue = 3 is burst mode.
#
# # -- set burst mode burst times:
# v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.MASTERPULSE_BURSTTIMES,
#                           fValue=10)
#
# # -- set master pulse trigger to be external trigger:
# v = dcam.prop_setgetvalue(idprop=DCAM_IDPROP.MASTERPULSE_TRIGGERSOURCE,
#                           fValue=1) # this sets the trigger source to be external.

# -- acquire


# -- capturing start:
dcam.cap_start()
# -- define timeout time
timeout_milisec = 300000
print(v)

t = datetime.datetime.now()
print(t)
t0=t
print('trying to change trigger source')
dcam.prop_setgetvalue(idprop=DCAM_IDPROP.TRIGGERSOURCE, fValue=1)  # 'INTERNAL'
t = datetime.datetime.now()
print('changing trigger source costs time:')
print(t-t0)
print('change it back')
dcam.prop_setgetvalue(idprop=DCAM_IDPROP.TRIGGERSOURCE, fValue=2)  # 'EXTERNAL'

# take 10 frames
t0 = datetime.datetime.now()
for frame_id in np.arange(10):
    print('\n frame number '+str(frame_id))
    # -- wait for the frame to be ready:
    dcam.wait_capevent_frameready(timeout_milisec)  # what does this time out mean?
    # -- read out the data from the buffer
    data = dcam.buf_getlastframedata()
    # change trigger to be internal
    dcam.prop_setgetvalue(idprop=DCAM_IDPROP.TRIGGERSOURCE, fValue=1)  # 'INTERNAL'
    # -- record and print the time
    t = datetime.datetime.now()
    print(t)
    print('time lapsed:')
    print(t-t0)
    t0 = t

# -- stop the capturing
dcam.cap_stop()

# dcam.prop_getvaluetext(idprop = DCAM_IDPROP.OUTPUTTRIGGER_BASESENSOR, fValue=2)

# release buffer
dcam.buf_release()

# close device
dcam.dev_close()

#un init the Dcamapi
Dcamapi.uninit()