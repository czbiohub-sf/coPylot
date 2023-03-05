from copylot.hardware.lights.abstract_light import AbstractLight

import serial
from serial import SerialException
from serial.tools import list_ports
import time
import sys
import logging

# from typing import TypeVar, Callable, Union, Any
# Setting up the Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Refer to manual for command details
#TODO: this probably is better if it's a dictionary and make 
GLOBAL_CMD = ['ECHO', 'PROMPT']
GLOBAL_QUERY = ['?BPT', '?H', '?IL', '?SFV', '?SPV']
LASER_CMD = ['C', 'DELAY', 'EPC', 'LC', 'LE', 'LP', 'PP', 'PUP']
LASER_QUERY = [
    '?C',
    '?CC',
    '?CT',
    '?DELAY',
    '?EPC',
    '?FC',
    '?FD',
    '?FP',
    '?FV',
    '?LC',
    '?LCS',
    '?LE',
    '?LH',
    '?LI',
    '?LP',
    '?LPS',
    '?LW',
    '?MAXP',
    '?OBT',
    '?OBTS',
    '?PP',
    '?PUL',
    '?RP',
]
VOLTRAN_CMDS = GLOBAL_CMD + GLOBAL_QUERY + LASER_CMD + LASER_QUERY


def get_lasers():
    com_ports = list_ports.comports()
    lasers = []
    try:
        for port in com_ports:
            try:
                laser = VoltranLaser(port=port.device)
                if laser.serial_number != None:
                    lasers.append((laser.port, laser.serial_number))
                    logger.info(f"Found: {laser.port}:{laser.devID}")
                    laser.disconnect()
                else:
                    raise Exception
            except:
                pass
        if len(lasers) < 1:
            raise Exception
        return lasers
    except:
        raise RuntimeError("No lasers found...")


class VoltranLaser(AbstractLight):
    def __init__(self, devID=None, port=None, baudrate=19200, timeout = 1):
        #Serial Communication
        self.port = port
        self.baudrate = baudrate
        self.address = None
        self.timeout = timeout
        
        #Laser Specs
        self.serial_number = devID
        self.part_num = None
        self.wavelength = None
        self.laser_shape = None

        #Properties
        self._curr_power = None
        self._ctrl_mode = None
        self._delay = None
        self._ext_power_ctrl = None
        self._current_ctrl = None
        self._toggle_emission = None
        self._pulse_power = None
        self._pulse_mode = None
        self._max_power = None

        self.connect()

    def connect(self):
        try:
            if self.port != None:
                try:
                    self.address = serial.Serial(
                        port=self.port,
                        baudrate=self.baudrate,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=self.timeout,
                    )
                    # self._echo_off()
                    self._identify_laser()
                except:
                    logger.debug(f"No Laser found in {self.port}")
            elif self.serial_number != None:
                ports = list_ports.comports()
                for port in ports:
                    try:
                        self.port = port
                        self.address = serial.Serial(
                            port=self.port,
                            baudrate=self.baudrate,
                            bytesize=serial.EIGHTBITS,
                            parity=serial.PARITY_NONE,
                            stopbits=serial.STOPBITS_ONE,
                            timeout=self.timeout,
                        )
                        self._identify_laser()
                        if devSN == self.serial_number:
                            logger.info(
                                f"Connected {self.port}: Laser: {self.devID}"
                            )
                        else:
                            self.disconnect()
                            raise Exception
                    except:
                        logger.debug(f"No laser found in {self.port}")
        except:
            raise RuntimeError("No laser found...")

    def disconnect(self):
        self.address.close()
        self.address = None

    def is_connected(self):
        logger.debug(f'{self.port} is open')
        return self.address.is_open

    def write_cmd(self, cmd, value=None):
        # All commands transmitted must terminate with a carriage return “\r” or 0x0D to be processed.
        try:
            if cmd in VOLTRAN_CMDS:
                if value != None:
                    cmd_LF = cmd + ' '+ str(value) + '\r'
                else:
                    cmd_LF = cmd +'\r'
                self.address.write(cmd_LF.encode('utf-8'))
                logger.debug(
                    f"Write to laser <{self.serial_number}> -> cmd:<{cmd.encode('utf-8')}>"
                )
                msg_out = self._read_cmd(cmd)
                return msg_out
            else:
                raise ValueError("Command not found")
        except Exception as e:
            raise RuntimeError("Error: sending command") from e

    def _read_cmd(self, cmd):
        # All replies to commands are in upper case.
        try:
            elapsed_time=0
            values = 0
            start_time = time.perf_counter()
            while elapsed_time < self.timeout :
                msg = self.address.readline().decode()
                elapsed_time = time.perf_counter() - start_time
                if len(msg)>1:
                    if msg.endswith('\n') or msg.endswith('\r'):
                        if (msg[ : len(cmd)+1] == (cmd + '=')):
                            values = msg[len(cmd)+1:-2].split(', ')
                            # logger.debug("msg_out > {msg}")
                            break
            logger.debug(f"Read: {values}")
            return values
        except:
            raise RuntimeError("Error: No response from laser")
    
    def _identify_laser(self):
        laser_param =  self.write_cmd('?LI')
        self.serial_number = laser_param[0]
        self.part_number = int(laser_param[1][:-2]) # [nm]
        self.wavelength = int(laser_param[2][:-2]) # [mW]
        self._max_power= float(laser_param[3][:-2])
        self.laser_shape = laser_param[4]
        logger.debug(f'Laser param: {laser_param}')
    
    # --------------------------------------------------------------------------------------------------

    # ---------------------------------------PROPERTIES-------------------------------------------------

    #TODO: implement table 9.3.4 from  PDF
    @property
    def drive_control_mode(self):
        return self._ctrl_mode
    @drive_control_mode.setter
    def set_control_mode(self, mode):
        self._ctrl_mode =  self.write_cmd('C', str(mode))[0]
    @drive_control_mode.getter
    def set_control_mode(self):
        self._ctrl_mode = self.write_cmd('?C')[0]
    
    @property
    def emission_delay (self):
        return self._delay
    @emission_delay.setter
    def set_emission_delay(self, mode):
        self._delay = self.write_cmd('DELAY', str(mode))[0]
    @emission_delay.getter
    def emission_delay (self):
        self._delay = self.write_control('?DELAY')[0]

    @property
    def external_power_control(self):
        return self._ext_power_ctrl
    @external_power_control.getter
    def external_power_control(self):
        self._ext_power_ctrl = self.write_cmd('?EPC')[0]
    @external_power_control.setter
    def set_external_power_control(self, control ):
        self._ext_power_ctrl =  self.write_cmd('EPC', str(control))[0]
    
    @property
    def current_control(self):
        return self._current_ctrl
    @current_control.getter
    def current_control(self):
        self._current_ctrl = self.write_cmd('?LC')[0]
    @current_control.setter
    def current_control(self, value):
        self._current_ctrl = self.write_cmd('LC', value)[0]

    @property
    def toggle_emission(self):
        return self._toogle_emission
    @toggle_emission.setter
    def toggle_emission(self, value):
        self._toggle_emission = self.write_cmd('LE', value)[0]
    @toggle_emission.getter
    def toggle_emission(self):
        self._toggle_emission = self.write_cmd('?LE')[0]

    def turn_on(self):
        logger.info('Turning laser: ON')
        self.toggle_emission = 1
        return self._toggle_emission
    def turn_off(self):
        logger.info('Turning laser: OFF')
        self.toggle_emission = 0
        return self._toggle_emission
    
    @property
    def laser_power(self):
        return self._curr_power
    @laser_power.getter
    def laser_power(self):
        self._curr_power =  float(self.write_cmd('?LP')[0])
        return self._curr_power
    @laser_power.setter
    def laser_power(self, power:float):
        if self._max_power is None:
            self.maximum_power
        if power > self._max_power:
            power = self._max_power
            logger.info(f'Maximum power is: {self._max_power}')
        logger.info(f'Setting power: {power}')
        self._curr_power = float(self.write_cmd('LP', power)[0])
        
    @property
    def pulse_power(self):
        return self._pulse_power
    @pulse_power.getter
    def pulse_power(self):
        self._pulse_power =float(self.write_cmd('?PP')[0])
    @pulse_power.setter
    def set_pulse_power(self, power):
        logger.info(f'Setting Power:{power}')
        self._pulse_power =  float(self.write_cmd('PP', str(power))[0])

    @property
    def pulse_mode(self):
        return self._pulse_mode
    @pulse_mode.getter
    def pulse_mode(self):
        self._pulse_mode = self.write_cmd('?PUL')[0]
    @pulse_mode.setter
    def set_pulse_mode(self, mode=0):
        self._pulse_mode =  self.write_cmd('PUL', str(mode))[0]
    
    @property
    def maximum_power(self)->float:
        return self._max_power
    @maximum_power.getter
    def maximum_power(self):
        self._max_power = float(self.write_cmd('?MAXP')[0])
    

    def _echo_off(self):
        self.write_cmd('ECHO', 0)
        logger.debug('Echo Off')

    def __enter__(self):
        return self

    def __exit__(self):
        self.switch_off()
        self.disconnect()

