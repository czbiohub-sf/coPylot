# %%
# from copylot.hardware.lasers.vortran import vortran_usb
import ctypes
from ctypes import cdll
import clr
import sys
import os

# %%
## This currently only works if the dlls are saved in root
#   TODO: Recompile the dll with the flag from below:
#    https://learn.microsoft.com/en-us/previous-versions/dotnet/netframework-4.0/dd409252(v=vs.100)?redirectedfrom=MSDN
# current_dir = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.join(current_dir, os.pardir))

# %%
# Load the .dll file
sys.path.append(r'C:\test_dll')
lib = clr.AddReference('StradusUSBHID')
# Import the namespace and classes from the .dll file
import StradusUSBHID
from StradusUSBHID import StradusHub

# %%
# Create an instance of the C# class and call the methods
hub = StradusHub()
hub.InitStradusHub()
num_lasers = hub.StradusCount
print(num_lasers)
print(f' num lasers {hub.get_StradusCount()}')

hub.StradusSend(0, '?li\r')
hub.StradusGetReply(0)

# %%
# Attempt with Ctypes to see if we can load the provided .dll
import ctypes

# Load the DLL
my_dll = ctypes.WinDLL(r'C:\test_dll\StradusUSBHID.dll')


##
# %%

#-----------------------------------------------------------------------------------------
#-------------------------------------------- USING THE HIDAPI python package--------------------------------------------
ANSWER_TIMEOUT = 20

def write_to_hid_device(device, buf):
    """
    Convenience function to write the buffer to the device. This does not take into account the 
    request types.
    Parameters
    ----------
    device : handle to the HID device
    buf : 64 bit buffer

    Returns: True if message sent properly
    """
    # Allocate a buffer that is one byte larger than the input buffer.
    report_buf = bytearray(len(buf) + 1)
    # Set the first byte of the report buffer to 0x0.
    report_buf[0] = 0x0
    # Copy the contents of the input buffer to the report buffer.
    report_buf[1:] = buf
    # Write the contents of the report buffer to the HID device.
    res = device.write(report_buf)
    # Check if the write operation was successful.
    if res < 0:
        print('ERROR" sending msg')
        return -1
    # Return the number of bytes written.
    return res

## Emulating what Vortran's Code does with their Fininte State Machine
from enum import Enum
class RequestTypes(Enum):
    SET_CMD_QRY = 0xA0
    GET_RESPONSE_STATUS = 0xA1
    GET_RESPONSE = 0xA2
    SET_RESPONSE_RECEIVED = 0xA3

def send_request(req_type, message):
    """
    Format the byte-array to be sent to vortran laser

    Parameters
    ----------
    req_type : Vortran request types
    message : string to send to HID device
    Returns: bytearray to be sent 
    """
    out_buffer = bytearray(65)
    if message is not None:
        request_out = bytes([req_type])
        out_buffer[
            0
        ] = 0x00  # The first byte is the "Report ID" and does not get sent over the USB bus. Always set = 0.
        out_buffer[1] = request_out[0]  # Control Byte, like vendor request
        out_buffer[2:64] = bytearray(
            [0xFF] * 62
        )  # Initialize the rest of the 64-byte packet to "0xFF"
        message = message.encode()
        out_buffer[
            2 : len(message) + 2
        ] = message  # Copy message to buffer starting at index 2
    return out_buffer

# %%
import hid
import time

for device_dict in hid.enumerate():
    keys = list(device_dict.keys())
    keys.sort()
    for key in keys:
        print("%s : %s" % (key, device_dict[key]))
    print()

# %%
try:
    print("Opening the device")

    h = hid.device()
    h.open(8218, 4097)  # VORTRAN VendorID/ProductID
    print("Manufacturer: %s" % h.get_manufacturer_string())
    print("Product: %s" % h.get_product_string())
    print("Serial No: %s" % h.get_serial_number_string())

    # # enable non-blocking mode
    h.set_nonblocking(1)

    # # write some data to the device
    print("Write the data")
    buff = send_request(RequestTypes.SET_CMD_QRY.value, "?LI\r")
    print(buff)
    h.write(buff)
    # buff = send_request(RequestTypes.SET_RESPONSE_RECEIVED.value, "")
    # h.write(buff)

    # # wait
    time.sleep(0.05)

    # # read back the answer
    print("Read the data")
    while True:
        d = h.read(65)
        if d[0] == RequestTypes.GET_RESPONSE.value:
            print('Getting response')
            print(d)
            # byte_string = bytes(d)  # Convert the list to a byte string
            # unicode_string = byte_string.decode('utf-8')  # Decode the byte string to a Unicode string
            # print(unicode_string)
        elif d[0] == RequestTypes.GET_RESPONSE_STATUS.value:
            print('Getting response statu exampls')
        else:
            print(d)
            break

    print("Closing the device")
    h.close()

except IOError as ex:
    print(ex)
    print("You probably don't have the hard-coded device.")
    print("Update the h.open() line in this script with the one")
    print("from the enumeration list output above and try again.")

print("Done")# %%

# %%
