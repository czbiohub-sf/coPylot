"""
controller the micropump (Bartels XU7 controller) to dispenser water to the water objective
useful serial commands:
bon         : turns pump on
boff        : turns pump off
f(1-300)    : set frequency, for example: f100
a(1-250)    : set amplitude, for example: a100
ms          : set signal to sine
mr          : set signal to rectangular
mc          : set signal to srs
(enter key) : display present settings
"""

import serial
import time


class WaterDispenserControl:
    def __init__(self, com, baudrate):
        self.stop_now = False
        self.com = com
        self.baudrate = baudrate

    def set_pump_speed(self, freq: int, amp: int):
        """set the speed for pump by setting the frequency and amplitude"""
        ser = serial.Serial(self.com, self.baudrate, timeout=5)
        if ser.is_open:
            ser.close()
        ser.open()
        message_freq = b"f" + bytearray(str(freq), "utf-8") + b"\r"
        print(message_freq)
        ser.write(message_freq)
        time.sleep(1)  # allow the pump to respond to previous command
        message_amp = b"a" + bytearray(str(amp), "utf-8") + b"\r"
        print(message_amp)
        ser.write(message_amp)
        ser.close()

    def run_pump(self, duration: float):
        """start pump for the duration and then stop"""
        ser = serial.Serial(self.com, self.baudrate, timeout=5)
        if ser.is_open:
            ser.close()
        ser.open()
        print("start dispensing water")
        ser.write(b"bon\r")
        time.sleep(duration)
        ser.write(b"boff\r")
        print("stop dispensing water")
        ser.close()

    def read_pump(self):
        """read out the current status and print"""
        ser = serial.Serial(self.com, self.baudrate, timeout=5)
        if ser.is_open:
            ser.close()
        ser.open()
        ser.write(b"\r")
        message = ser.read(100)
        print(message.decode("utf-8"))
        ser.close()

    def run_for_recording(self, interval: float, duration: float, freq: int, amp: int):
        """run the pump for a recording session
        interval: float, unit: minute, interval to wait to run pump again
        duration: fload, unit: second, duration when pump is on
        freq: int, pump control frequency
        amp : int, pump control amplitude
        """
        waittime = interval * 60 - duration
        if waittime <= 0:
            raise ValueError("interval is shorter than duration")

        self.set_pump_speed(freq, amp)  # set the pump speed
        time.sleep(1)
        while not self.stop_now:
            self.run_pump(duration)
            time.sleep(waittime)
