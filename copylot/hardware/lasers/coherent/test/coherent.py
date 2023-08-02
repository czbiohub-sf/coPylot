import time
from serial import SerialException
from copylot import logger
from copylot.hardware.lasers.abstract_laser import AbstractLaser
import serial
'''
This code build based on a copy of the coherent.py file form Dr. Peter Kner at the University of Georgia.
@author: Yang Liu
'''

# -*- coding: utf-8 -*-


class CoherentLaser(AbstractLaser):

    def __init__(self, portS='COM4'):
        try:
            self.ser = serial.Serial(
                port=portS,
                baudrate=19200,
                parity=serial.PARITY_NONE,
                stopbits=1,
                bytesize=8
                #            stopbits=serial.STOPBITS_ONE,
                #            bytesize=serial.EIGHTBITS
            )
            self.res = 0
            res = self.ser.portstr  # check which port was really used
            if res == portS:
                print('Port Connected')
            else:
                raise Exception('Port Not Connected')
        except SerialException:
            self.ser.close()
            print('port already open')
        print('Model: ')
        print(self.RW('SYSTem:INFormation:MODel?'))
        print(self.RW('SYSTem:INFormation:TYPe?'))
        print(self.RW('SYSTem:INFormation:PNUMber?'))
        self.num_wavelength = int(self.RW('SYSTem:INFormation:PORTs?'))
        print('Number of Wavelength: %d' % self.num_wavelength)
        for i in range(self.num_wavelength):
            print('Wavelength %d: ' % (i+1))
            print(self.GetWaveLength(i+1))
            print('Operating Hours: ')
            print(self.RW('SYSTem%d:HOURs?' % (i+1)))
            print('Maximum Power: ')
            print(self.RW('SOURce%d:POWer:LIMit:HIGH?' % (i+1)))
            print(self.IsLaserOn())
        self.maxpower = self.RW('SOURce1:POWer:LIMit:HIGH?')
        time.sleep(0.1)

    def __del__(self):
        print('closing laser')
        self.SetLaserOff()
        self.ser.close()

    def GetPower(self):
        output = self.RW('SOURce:POWer:LEVel?')
        self.power = float(output)
        return output

    def SetPowerLevel(self, power):
        if power > self.maxpower:
            raise Exception('Max power is %f!' % self.maxpower)
        else:
            self.RW('SOURce:POWer:LEVel:IMMediate:AMPLitude %3.3f' % power)
            return self.err
    def GetWaveLength(self,channel=1):
        cmd = 'SYSTem%d:INFormation:WAVelength?' % channel
        output = self.RW(cmd)
        return output
    def IsLaserOn(self,channel=1):
        state = self.RW('SOURce%d:AM:STATe?' % channel)
        if state == 'OFF':
            self.laser_on = False
        else:
            self.laser_on = True
        return state

    def SetLaserOn(self):
        if not self.laseron:
            self.RW('SOUR:AM:STAT ON')
            self.laseron = True
        return True

    def SetLaserOff(self):
        if self.laseron:
            self.RW('SOUR:AM:STAT OFF')
            self.laseron = False
        return True

    def SetCWPowerMode(self):
        self.RW('SOURce:AM:INTernal CWP')
        return self.err

    def SetDigitalModMode(self):
        self.RW('SOURce:AM:EXTernal DIGital')
        return self.err

    def QueryLaserMode(self):
        out = self.RW('SOURce:AM:SOURce?')
        return out

    def GetLaserStatus(self):
        ''' 'C8001088'
            '80000000' '''
        stat = self.RW('SYSTem:INFormation:ENUMeration?')
        stat = self.dec2bin(stat)
        # fault = self.RW('SYST:FAUL?')
        return (stat)

    def RW(self, command):
        self.ser.flushInput()
        ser_command = '%s\r' % command
        self.ser.write(ser_command.encode())
        time.sleep(0.1)
        res = self.ser.read(self.ser.inWaiting()).decode()
        n1 = res.find('<')
        n2 = res.find('\r')
        self.err = res[n2 + 1:].rstrip('\r\n').lstrip('\r\n')
        result = res[n1 + 1:n2]
        return result

    def dec2bin(self,number: int):
        ans = ""
        if (number == 0):
            return 0
        while (number):
            ans += str(number & 1)
            number = number >> 1
        ans = ans[::-1]
        return ans