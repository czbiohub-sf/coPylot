"""
@author:edyoshikun

vortran Stradus Laser python wrapper using RS-232 -> COM device.

For more details regarding operation,
refer to the manuals in https://www.vortranlaser.com/

"""
from copylot.hardware.lasers.abstract_laser import AbstractLaser
import serial
from serial.tools import list_ports
import time
import logging

# Setting up the Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s -\
                                 %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


class VortranLaser(AbstractLaser):
    # TODO: this probably is better if it's a dictionary and make
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

    def __init__(
        self, serial_number=None, port=None, baudrate=19200, timeout=1
    ):
        """
        Wrapper for vortran stradus lasers.
        establishes a connection through COM port

        Default paramters taken from documentation
        Parameters
        ----------
        device_id : str
            serial number for the device
        port : serial
            COM port the device is connected
        baudrate : int
           baudrate for serial communication
        timeout : int
            timeout for write/read in seconds
        """
        # Serial Communication
        self.port: str = port
        self.baudrate: int = baudrate
        self.address = None
        self.timeout: int = timeout

        # Laser Specs
        self.serial_number: str = None
        self.part_num: int = None
        self.wavelength: int = None
        self.laser_shape: str = None
        self._in_serial_num = serial_number

        # Properties
        self._curr_power = None
        self._ctrl_mode = None
        self._delay = None
        self._ext_power_ctrl = None
        self._current_ctrl = None
        self._toggle_emission = None
        self._pulse_power = None
        self._pulse_mode = None
        self._max_power = None
        self._is_connected = None

        self.connect()

    def connect(self):
        """
        Establish the serial communication with the device in COM port

        Retrieves information about the laser including:
        - serial number
        - part number
        - wavelength
        - maximum power
        - beam shape

        """
        try:
            if self.port is not None:
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
                except RuntimeError:
                    logger.debug(f"No Laser found in {self.port}")
            elif self._in_serial_num is not None:
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
                        if self._in_serial_num == self.serial_number:
                            logger.info(
                                f"Connected {self.port}: \
                                Laser: {self.serial_number}"
                            )
                        else:
                            self.disconnect()
                            raise Exception
                    except RuntimeError:
                        logger.debug(f"No laser found in {self.port}")
            else:
                list_lasers = VortranLaser.get_lasers()
                for i in len(list_lasers):
                    port = list_lasers[i][0]
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
                        if self._in_serial_num == self.serial_number:
                            logger.info(
                                f"Connected {self.port}: \
                                Laser: {self.serial_number}"
                            )
                        else:
                            self.disconnect()
                            raise Exception
                    except RuntimeError:
                        logger.debug(f"No laser found in {self.port}")
        except RuntimeError:
            logger.info(f"No laser found in {self.port}")

    def disconnect(self):
        """
        Disconnects the device
        """
        self.address.close()
        self.address = None

    @property
    def is_connected(self):
        """
        Check if device is connected to COM Port and return True/False

        """
        logger.debug(f'{self.port} is open')
        return self._is_connected

    @is_connected.getter
    def is_connected(self):
        """
        Check if device is connected to COM Port and return True/False

        """
        self._is_connected = self.address.is_open

    def _write_cmd(self, cmd, value=None):
        """
        Writes the commands to the device

        All commands transmitted must terminate with a
        carriage return “\r” or 0x0D to be processed.

        Parameters
        ----------
        cmd : 'str'
            vortran Stadus command
        value : (int,float,str)
            value to be set with command

        Returns
        -------
        a list with the parsed response from the device to the given command
        """
        try:
            if cmd in VortranLaser.VOLTRAN_CMDS:
                if value is not None:
                    cmd_LF = cmd + '=' + str(value) + '\r'
                else:
                    cmd_LF = cmd + '\r'
                self.address.write(cmd_LF.encode('utf-8'))
                logger.debug(
                    f"Write to laser <{self.serial_number}> \
                    -> cmd:<{cmd.encode('utf-8')}>"
                )
                msg_out = self._read_cmd(cmd)
                return msg_out
            else:
                raise ValueError("Command not found")
        except Exception as e:
            raise RuntimeError("Error: sending command") from e

    def _read_cmd(self, cmd):
        """
        Reads the data from the serial port and parses the data in response
        to a sent command

        Parameters
        ----------
        cmd : (str)
            the command written
        Returns
        -------
            the decoded and parsed response to the command
        """
        # All replies to commands are in upper case.
        try:
            elapsed_time = 0
            values = None
            start_time = time.perf_counter()
            while elapsed_time < self.timeout:
                msg = self.address.readline().decode()
                elapsed_time = time.perf_counter() - start_time
                if len(msg) > 1:
                    if msg.endswith('\n') or msg.endswith('\r'):
                        if msg[: len(cmd) + 1] == (cmd + '='):
                            values = msg[len(cmd) + 1 : -2].split(', ')
                            # logger.debug("msg_out > {msg}")
                            break
            logger.debug(f"Read: {values}")
            if values is None:
                values = ['0']
                # TODO: maybe raise warning?
                # raise Warning
            return values
        except RuntimeWarning:
            logger.info("Error: No response from laser")

    def _identify_laser(self):
        """
        Helper function to identify the parameters for the connected laser.
        Updates the laser information
        (i.e serial number, wavelength,
        part number, max power, and laser shape)
        """
        laser_param = self._write_cmd('?LI')
        self.serial_number = laser_param[0]
        self.part_number = int(laser_param[1][:-2])  # [nm]
        self.wavelength = int(laser_param[2][:-2])  # [mW]
        self._max_power = float(laser_param[3][:-2])
        self.laser_shape = laser_param[4]
        logger.debug(f'Laser param: {laser_param}')

    # --------------------------------------------------------------------------------------------------

    # ---------------------------------------PROPERTIES-------------------------------------------------

    # TODO: implement table 9.3.4 from  PDF
    @property
    def drive_control_mode(self):
        """
        Laser Drive Control Mode
        Sets Power or Current Control
        (1 = Current Control)
        """
        return self._ctrl_mode

    @drive_control_mode.setter
    def set_control_mode(self, mode):
        """
        Laser Drive Control Mode
        Sets Power or Current Control
        (1 = Current Control)
        (0 = Power Control)

        """
        self._ctrl_mode = self._write_cmd('C', str(mode))[0]

    @drive_control_mode.getter
    def get_control_mode(self):
        """
        Laser Drive Control Mode
        Gets Power or Current Control
        (1 = Current Control)
        (0 = Power Control)
        """
        self._ctrl_mode = self._write_cmd('?C')[0]

    @property
    def emission_delay(self):
        """
        Toggle 5 Second Laser Emission Delay On and Off
        (1 = On, 0 = Off)
        """
        return self._delay

    @emission_delay.setter
    def set_emission_delay(self, mode):
        """
        Toggle 5 Second Laser Emission Delay On and Off
        (1 = On, 0 = Off)
        """
        self._delay = self._write_cmd('DELAY', str(mode))[0]

    @emission_delay.getter
    def emission_delay(self):
        """
        Toggle 5 Second Laser Emission Delay On and Off
        (1 = On, 0 = Off)
        """
        self._delay = self.write_control('?DELAY')[0]

    @property
    def external_power_control(self):
        """
        Enables External Power Control
        (1= External Control)
        """
        return self._ext_power_ctrl

    @external_power_control.getter
    def external_power_control(self):
        """
        Enables External Power Control
        (1= External Control, 0 = Off)
        """
        self._ext_power_ctrl = self._write_cmd('?EPC')[0]

    @external_power_control.setter
    def set_external_power_control(self, control):
        """
        Enables External Power Control
        (1= External Control, 0 = Off)
        """
        self._ext_power_ctrl = self._write_cmd('EPC', str(control))[0]

    @property
    def current_control(self):
        """
        Laser Current Control (0-Max)
        """
        return self._current_ctrl

    @current_control.getter
    def current_control(self):
        """
        Laser Current Control (0-Max)
        """
        self._current_ctrl = self._write_cmd('?LC')[0]

    @current_control.setter
    def current_control(self, value):
        """
        Laser Current Control (0-Max)
        """
        self._current_ctrl = self._write_cmd('LC', value)[0]

    @property
    def toggle_emission(self):
        """
        Toggles Laser Emission On and Off
        (1 = On, 0 = Off)
        """
        return self._toogle_emission

    @toggle_emission.setter
    def toggle_emission(self, value):
        """
        Toggles Laser Emission On and Off
        (1 = On, 0 = Off)
        """
        self._toggle_emission = self._write_cmd('LE', value)[0]

    @toggle_emission.getter
    def toggle_emission(self):
        """
        Toggles Laser Emission On and Off
        (1 = On, 0 = OffFFF)
        """
        self._toggle_emission = self._write_cmd('?LE')[0]

    def turn_on(self):
        """
        Alias function that toggles Laser Emission ON
        """
        logger.info('Turning laser: ON')
        self.toggle_emission = 1
        return self._toggle_emissionF

    def turn_off(self):
        """
        Alias function that toggles Laser Emission Off
        """
        logger.info('Turning laser: OFF')
        self.toggle_emission = 0
        return self._toggle_emission

    @property
    def laser_power(self):
        """
        Sets the laser power
        Requires pulse_mode() to be OFF
        """
        return self._curr_power

    @laser_power.getter
    def laser_power(self):
        """
        Sets the laser power
        Requires pulse_mode() to be OFF
        """
        self._curr_power = float(self._write_cmd('?LP')[0])
        return self._curr_power

    @laser_power.setter
    def laser_power(self, power: float):
        """
        Sets the laser power
        Requires pulse_mode() to be OFF
        """
        if self._max_power is None:
            self.maximum_power
        if power > self._max_power:
            power = self._max_power
            logger.info(f'Maximum power is: {self._max_power}')
        logger.info(f'Setting power: {power}')
        self._curr_power = float(self._write_cmd('LP', power)[0])

    @property
    def pulse_power(self):
        """
        Pulse Power configuration
        Requires pulse_mode() to be ON
        """
        return self._pulse_power

    @pulse_power.getter
    def pulse_power(self):
        """
        Pulse Power configuration
        """
        self._pulse_power = float(self._write_cmd('?PP')[0])

    @pulse_power.setter
    def set_pulse_power(self, power):
        """
        Pulse Power configuration
        """
        logger.info(f'Setting Power:{power}')
        self._pulse_power = float(self._write_cmd('PP', str(power))[0])

    @property
    def pulse_mode(self):
        """
        Toggle Pulse Mode On and Off (1=On)
        """
        return self._pulse_mode

    @pulse_mode.getter
    def pulse_mode(self):
        """
        Toggle Pulse Mode On and Off (1=On)
        """
        self._pulse_mode = self._write_cmd('?PUL')[0]

    @pulse_mode.setter
    def set_pulse_mode(self, mode=0):
        """
        Toggle Pulse Mode On and Off (1=On)
        """
        self._pulse_mode = self._write_cmd('PUL', str(mode))[0]

    @property
    def maximum_power(self) -> float:
        """
        Request Maximum Laser Power
        """
        return self._max_power

    @maximum_power.getter
    def maximum_power(self):
        """
        Request Maximum Laser Power
        """
        self._max_power = float(self._write_cmd('?MAXP')[0])

    def _echo_off(self):
        self._write_cmd('ECHO', 0)
        logger.debug('Echo Off')

    @staticmethod
    def get_lasers():
        com_ports = list_ports.comports()
        lasers = []
        try:
            for port in com_ports:
                try:
                    laser = VortranLaser(port=port.device)
                    if laser.serial_number is not None:
                        lasers.append((laser.port, laser.serial_number))
                        logger.info(
                            f"Found: {laser.port}:{laser.serial_number}"
                        )
                        laser.disconnect()
                    else:
                        raise Exception
                except RuntimeWarning:
                    logger.debug(f'No laser found in {port}')
            if len(lasers) < 1:
                raise Exception
            return lasers
        except RuntimeError:
            logger.info("No lasers found...")
