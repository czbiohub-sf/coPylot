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
        '''
        Initialize the laser.

        Parameters
        ----------
        portS
        The port number of the laser. Default is COM4.

        '''
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
            print('Wavelength %d: ' % (i + 1))
            print(self.GetWaveLength(i + 1))
            print('Operating Hours: ')
            print(self.RW('SYSTem%d:HOURs?' % (i + 1)))
            print('Maximum Power: ')
            print(self.RW('SOURce%d:POWer:LIMit:HIGH?' % (i + 1)))
            print(self.IsLaserOn())
        self.max_power = self.RW('SOURce1:POWer:LIMit:HIGH?')
        time.sleep(0.1)

    def __del__(self):
        ''''
        close the laser
        '''
        print('closing laser')
        self.SetLaserOff()
        self.ser.close()

    def GetPower(self, channel=1):
        '''
        Get the power of the laser

        Parameters
        ----------
        channel
        The channel of the laser
        1: 405nm
        2: 488nm
        3: 561nm
        4: 640nm

        Returns
        -------
        output : float
        The power of the laser
        '''
        cmd = 'SOURce%d:POWer:LEVel?' % channel
        output = self.RW(cmd)
        self.power = float(output)
        return output

    def SetPowerLevel(self, power,channel=1):
        '''
        Set the power of the laser
        Parameters
        ----------
        power
        The power of the laser
        channel
        The channel of the laser
        1: 405nm
        2: 488nm
        3: 561nm
        4: 640nm


        Returns
        -------

        '''
        if power > self.maxpower:
            raise Exception('Max power is %f!' % self.maxpower)
        else:
            cmd = 'SOURce%d:POWer:LEVel:IMMediate:AMPLitude %3.3f' % (channel, power)
            self.RW(cmd)
            return self.err

    def GetWaveLength(self, channel=1):
        '''
        Get the wavelength of the laser
        Parameters
        ----------
        channel
        The channel of the laser
        1: 405nm
        2: 488nm
        3: 561nm
        4: 640nm

        Returns
        -------
        output : float
        The wavelength of the laser
        '''
        cmd = 'SYSTem%d:INFormation:WAVelength?' % channel
        output = self.RW(cmd)
        return output

    def IsLaserOn(self, channel=1):
        '''
        Check if the laser is on
        Parameters
        ----------
        channel
        The channel of the laser
        1: 405nm
        2: 488nm
        3: 561nm
        4: 640nm


        Returns
        -------
        state : string
        The state of the laser

        '''
        cmd = 'SOURce%d:AM:STATe?' % channel
        state = self.RW(cmd)
        if state == 'OFF':
            self.laser_on = False
        else:
            self.laser_on = True
        return state

    def SetLaserOn(self, channel=1):
        '''
        Turn on the laser
        Parameters
        ----------
        channel
        The channel of the laser
        1: 405nm
        2: 488nm
        3: 561nm
        4: 640nm


        Returns
        -------
        error code

        '''
        cmd = 'SOURce%d:AM:STATe ON' % channel
        if not self.laser_on:
            self.RW(cmd)
            self.laser_on = True
        return True

    def SetLaserOff(self, channel=1):
        '''
        Turn off the laser
        Parameters
        ----------
        channel
        The channel of the laser
        1: 405nm
        2: 488nm
        3: 561nm
        4: 640nm

        Returns
        -------
        error code

        '''
        cmd = 'SOURce%d:AM:STATe OFF' % channel
        if self.laser_on:
            self.RW(cmd)
            self.laser_on = False
        return True

    def SetCWPowerMode(self, channel=1):
        '''
         Parameters
        ----------
        channel
        The channel of the laser
        1: 405nm
        2: 488nm
        3: 561nm
        4: 640nm

        Returns
        -------
        error code
        '''
        cmd = 'SOURce%d:AM:INTernal CWP' % channel
        self.RW('cmd')
        return self.err

    def SetDigitalModMode(self, channel=1):
        '''

        Parameters
        ----------
        channel
        The channel of the laser
        1: 405nm
        2: 488nm
        3: 561nm
        4: 640nm

        Returns
        -------
        error code
        '''
        cmd = 'SOURce%d:AM:INTernal DIGital' % channel
        self.RW(cmd)
        return self.err

    def QueryLaserMode(self, channel=1):
        '''

        Parameters
        ----------
        channel

        Returns
        -------
        'CWP' or 'DIGITAL' or 'ANALOG' or 'MIXED'
        '''
        cmd = 'SOURce%d:AM:SOURce?' % channel
        out = self.RW(cmd)
        return out

    def GetLaserStatus(self):
        '''
        Check the status of channels

        orders in 640, 561, 488, 405 [4,3,2,1]


        Returns
        -------

        '''
        stat = self.RW('SYSTem:INFormation:ENUMeration?')
        stat = self.dec2bin(stat)
        # fault = self.RW('SYST:FAUL?')
        return stat

    def RW(self, command):
        ''''
        Read and write the command to the laser
        all commands transmitted must terminate with a
        carriage return “\r” or 0x0D to be processed.

        Parameters
        ----------
        command :
            'str'
            coherent command to be sent to the laser
        Returns
        -------
        a parsed response from the device to the given command
        '''
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

    def dec2bin(self, number: int):
        '''
        Convert decimal number to binary number
        Parameters
        ----------
        number
        The decimal number

        Returns
        -------
        ans : string

        '''
        ans = ""
        if (number == 0):
            return 0
        while (number):
            ans += str(number & 1)
            number = number >> 1
        ans = ans[::-1]
        return ans


