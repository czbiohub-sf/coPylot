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

#%%
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
