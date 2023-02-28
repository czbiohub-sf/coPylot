# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 11:20:41 2020

@author: Yang Liu 
"""

import time
import optoMDC
import os
import sys
import numpy as np



class optomirror(object):

    def connect(self):
        self.mirror1 = optoMDC.connect('COM25')# back pupil plane
        #
        self.m1_ch_0 = self.mirror1.Mirror.Channel_0
        self.m1_ch_1 = self.mirror1.Mirror.Channel_1
        self.m1_ch_0.SetControlMode(optoMDC.Units.XY)
        self.m1_ch_1.SetControlMode(optoMDC.Units.XY)
        self.m1_ch_0.StaticInput.SetAsInput()
        self.m1_ch_1.StaticInput.SetAsInput()
        self.mirror2 = optoMDC.connect('COM6')# image plane
        self.m2_ch_0 = self.mirror2.Mirror.Channel_0
        self.m2_ch_1 = self.mirror2.Mirror.Channel_1
        self.m2_ch_0.SetControlMode(optoMDC.Units.XY)
        self.m2_ch_1.SetControlMode(optoMDC.Units.XY)
        self.m2_ch_0.StaticInput.SetAsInput()
        self.m2_ch_1.StaticInput.SetAsInput()
        return ("mirror connected")
#        self.bpp_ref = np.array([-0.035,-0.007])
#        self.img_ref = np.array([-0.001,-0.008])
#        self.SetMirror_1(self.bpp_ref)
#        self.SetMirror_2(self.img_ref)

    
    def SetMirror_1_ch0(self,value):
        self.m1_ch_0.StaticInput.SetXY(value)
        return ('M1c0 Set')
    
    def SetMirror_1_ch1(self,value):
        self.m1_ch_1.StaticInput.SetXY(value)
        return ('M1c1 Set')
    
    def SetMirror_2_ch0(self,value):
        self.m2_ch_0.StaticInput.SetXY(value)
        return ('M2c0 Set')
    
    def SetMirror_2_ch1(self,value):
        self.m2_ch_1.StaticInput.SetXY(value)
        return ('M2c1 Set')
        
            
#    def scanXYbpp(self,params):
#        '''stepSize is XY unit, numsteps decide the range and grid size, inip initial position'''
#        value0=params[0]
#        value1=params[1]
#        stepSize = params[2]
#        numsteps = params[3]
#        stepangle=np.arctan(stepSize*np.tan(50*np.pi/180)) # step angle in radian
#        angle =stepangle*180/np.pi
#        stepinmicron=stepangle*100*75/100*12.5/100*1000 # step beam in microns
#        print('stepangle: %s' %angle)
#        print('stepsize in microns: %s' %stepinmicron)
#        xvalue = np.around(np.arange(value0,value0+numsteps*stepSize,stepSize),decimals=4)
#        yvalue =np.around(np.arange(value1,value1+numsteps*stepSize,stepSize),decimals=4)
#        self.Points = np.array(list(itertools.product(xvalue,yvalue)))
#        for i in np.arange(len(self.Points)):
#            temp = self.Points[i]
#            print(temp)
#            temp = list(temp)
#            self.sig_mirrorcalir.emit(temp)

    
    def diconnect(self):
        self.mirror1.disconnect()
        self.mirror2.disconnect()
        return ("mirror disconnected")
        
#    
#    def SetMirror_1(self,setting):
#        time1 = time.perf_counter()
#        value0= setting[0]
#        value1= setting[1]
#        self.m1_ch_1.StaticInput.SetXY(value0)
#        time.sleep(0.3)
#        self.m1_ch_0.StaticInput.SetXY(value1)
#        t = time.perf_counter()-time1
#        #print (t)
        
#    def SetMirror_2(self,setting):
#        value0= setting[0]
#        value1= setting[1]
#        self.m2_ch_0.StaticInput.SetXY(value0)
#        time.sleep(0.3)
#        self.m2_ch_1.StaticInput.SetXY(value1)
    
    def getMirror_1(self):
        self.m1c0 = self.m1_ch_0.StaticInput.GetXY()
        self.m1c1 = self.m1_ch_1.StaticInput.GetXY()
        value =self.m1c0 + self.m1c1
        return value
        
    def getMirror_2(self):
        self.m2c0 = self.m2_ch_0.StaticInput.GetXY()
        self.m2c1 = self.m2_ch_1.StaticInput.GetXY()
        value = self.m2c0+self.m2c1
        return value
        
        
Opto_Mirror = optomirror()

def disconnectmirror():
    return Opto_Mirror.diconnect()

def connectmirror():
    return Opto_Mirror.connect()

def getMirror1():
    return Opto_Mirror.getMirror_1()

def getMirror2():
    return Opto_Mirror.getMirror_2()

def SetMirror1ch0(value):
    return Opto_Mirror.SetMirror_1_ch0(value)

def SetMirror1ch1(value):
    return Opto_Mirror.SetMirror_1_ch1(value)

def SetMirror2ch0(value):
    return Opto_Mirror.SetMirror_2_ch0(value)

def SetMirror2ch1(value):
    return Opto_Mirror.SetMirror_2_ch1(value)
    
        
