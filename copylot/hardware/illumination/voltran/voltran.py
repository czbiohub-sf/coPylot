import serial
from serial.tools import list_ports
import time
import syst
import logging

# from typing import TypeVar, Callable, Union, Any
logger = logging.basicConfig(
    level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s'
)

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
        for port in comp_ports:
            laser = CoboltLaser(port=port.device)
            if laser != None:
                lasers.append((port, laser.devID))
        if len(lasers) > 0:
            for port, SN in lasers:
                logging.info("fCOM{port}:{SN}")
            return port, lasers
        else:
            raise RuntimeError("No lasers found...")
    except:
        raise RuntimeError("No lasers found...")


class VoltranLaser:
    def __init__(self, devID=None, port=None, baudrate=19200):
        self.devID = devID
        self.port = port
        self.baudrate = baud
        self.address = None
        self.connect()
        self.max_power = None

    def connect(self):
        try:
            ports = list_comports.comports()
            if self.port == None:
                raise RuntimeError("COM port not selected")
            for port in ports:
                devSN = self.write_cmd("?LI")
                if self.devID == devSN:
                    self.port = port
                    self.address = serial.Serial(
                        port=self.port,
                        baudrate=self.baud,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=2,
                    )
                    logging.info(f"Connected COM{self.port}: Laser: {self.devID} ")
        except:
            raise RuntimeError("No laser found...")

    def disconnect(self):
        self.address.close()

    def is_connected(self):
        return self.address.is_open()

    def _get_serial_num(self):
        try:
            self.devID = self.write_cmd('?')
        except:
            self.disconnect()
            raise RuntimeError("This is not a laser")

    def write_cmd(self, msg):
        # All commands transmitted must terminate with a carriage return “\r” or 0x0D to be processed.
        msg += '/r'
        try:
            if msg in VOLTRAN_CMDS:
                self.address.write(msg.encode())
                logging.debug(
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
                    logging.debug(
                        "Read from laser<{self.devID}> -> msg:<{msg_received}>"
                    )
                    return msg_received
                else:
                    raise RuntimeError("Error: No response from laser")
            else:
                raise RuntimeError("Error: No response from laser")
        except:
            raise RuntimeError("Error: No response from laser")

    def get_power(self):
        return self.write_cmd('?LP')

    def set_power(self, power):
        if self.max_power is None:
            self.max_power = self.max_power()
        if power > self.max_power:
            power = self.max_power
            logging.info(f'Maximum power is: {self.max_power}')
        logging.info(f'Setting power: {power}')
        return self.write_cmd(f'LP {power}')

    def set_pulse_power(self, power):
        logging.info(f'Setting Power:{power}')
        return self.write_cms(f'PP {power}')

    def pulse_mode(self, mode=0):
        return self.write_cmd('PUL')

    def max_power(self):
        return int(self.write_cmd('?MAXP'))

    def turn_on(self):
        logging.info('Turning laser: ON')
        return self.write_cmd('LE 1')

    def turn_off(self):
        logging.info('Turning laser: OFF')
        return self.write_cmd('LE 0')

    def __enter__(self):
        return self

    def __exit__(self):
        self.switch_off()
        self.disconnect()
