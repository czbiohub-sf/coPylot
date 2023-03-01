from copylot.hardware.mirrors.optotune import optoMDC


class OptoMirror:
    def __init__(self, com_port: str = None):
        self.mirror = optoMDC.connect(
            com_port if com_port is not None else "COM3"
        )

        self.channel_x = self.mirror.Mirror.Channel_0
        self.channel_x.SetControlMode(optoMDC.Units.XY)
        self.channel_x.StaticInput.SetAsInput()

        self.channel_y = self.mirror.Mirror.Channel_1
        self.channel_y.SetControlMode(optoMDC.Units.XY)
        self.channel_y.StaticInput.SetAsInput()
        print("mirror connected")

    def __del__(self):
        self.mirror.disconnect()
        print("mirror disconnected")

    @property
    def positions(self):
        return self.position_x, self.position_y

    @property
    def position_x(self):
        """

        Returns
        -------

        """
        return self.channel_x.StaticInput.GetXY()[0]

    @position_x.setter
    def position_x(self, value):
        """

        Parameters
        ----------
        value

        """
        self.channel_x.StaticInput.SetXY(value)
        print('M1c0 Set')

    @property
    def position_y(self):
        return self.channel_y.StaticInput.GetXY()[0]

    @position_y.setter
    def position_y(self, value):
        self.channel_y.StaticInput.SetXY(value)
        print('M1c1 Set')


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
