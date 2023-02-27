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
                if laser.devID != None:
                    lasers.append((port, laser.devID))
                    logging.info("fCOM{laser.port}:{laser.devID}")
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
    def __init__(self, devID=None, port=None, baudrate=19200):
        self.devID = devID
        self.port = port
        self.baudrate = baudrate
        self.address = None
        self.max_power = None
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
                        timeout=1,
                    )
                    # TODO: probably this command can be anything that generates a response?
                    devSN = self.write_cmd("?LI")
                    if len(devSN) > 1:
                        self.devID = devSN
                except:
                    logging.debug(f"No Laser found in COM {self.port}")
            elif self.devID != None:
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
                            timeout=1,
                        )
                        devSN = self.write_cmd("?LI")
                        if devSN == self.devID:
                            logging.info(
                                f"Connected COM{self.port}: Laser: {self.devID} "
                            )
                        else:
                            self.disconnect()
                            raise Exception
                    except:
                        logging.debug(f"No laser found in COM{self.port}")
        except:
            raise RuntimeError("No laser found...")

    def disconnect(self):
        self.address.close()
        self.address = None

    def is_connected(self):
        return self.address.is_open()

    def write_cmd(self, msg):
        # All commands transmitted must terminate with a carriage return “\r” or 0x0D to be processed.
        try:
            if msg in VOLTRAN_CMDS:
                msg += '/r'
                self.address.write(msg.encode('utf-8'))
                logger.debug(
                    f"Write to laser <{self.devID}> -> cmd:<{msg.encode('utf-8')}>"
                )
            else:
                raise ValueError("Command not found")
            msg = self._read_cmd()
            return msg
        except Exception as e:
            raise RuntimeError("Error: sending command") from e

    def _read_cmd(self):
        # All replies to commands are in upper case.
        # Replies begin with carriage return, newline “/r/n” or 0x0D, 0x0A.
        try:
            msg_received = self.address.readline().decode('utf-8')
            if len(msg_received) > 1:
                if msg_received[-2] == '/n':
                    msg_received = msg_received[2:]
                    logger.debug(
                        "Read from laser<{self.devID}> -> msg:<{msg_received}>"
                    )
                    return msg_received
                else:
                    raise RuntimeError("Error: No response from laser")
            else:
                raise RuntimeError("Error: No response from laser")
        except:
            raise RuntimeError("Error: No response from laser")

    def set_laser_control_mode(self, mode):
        return self.write_cmd(f'C {mode}')

    def set_emission_delay(self, mode):
        return self.write_cmd(f'DELAY {mode}')

    def set_external_power_control(self, control ):
        return self.write_cmd(f'EPC {control}')
        
    def set_power(self, power):
        if self.max_power is None:
            self.max_power = self.max_power()
        if power > self.max_power:
            power = self.max_power
            logger.info(f'Maximum power is: {self.max_power}')
        logger.info(f'Setting power: {power}')
        return self.write_cmd(f'LP {power}')

    def set_pulse_power(self, power):
        logger.info(f'Setting Power:{power}')
        return self.write_cms(f'PP {power}')

    def set_pulse_mode(self, mode=0):
        return self.write_cmd(f'PUL {mode}')

    def max_power(self):
        return int(self.write_cmd('?MAXP'))

    def turn_on(self):
        logger.info('Turning laser: ON')
        return self.write_cmd('LE 1')

    def turn_off(self):
        logger.info('Turning laser: OFF')
        return self.write_cmd('LE 0')
    
    def set_control_mode(self, mode):
        return self.write_cmd(f'C {mode}')

    #TODO: implement table 9.3.4 from  PDF
    def get_power(self):
        return self.write_cmd('?LP')


    def __enter__(self):
        return self

    def __exit__(self):
        self.switch_off()
        self.disconnect()
