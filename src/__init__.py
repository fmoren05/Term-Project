"""
@file __init__.py
@brief Controls the MLX90640 thermal infrared camera.

@details
This file contains a class which manages an MLX90640 thermal infrared camera.
It provides functionalities to control the camera and obtain raw data.

@author
Dr. Ridgely

Modified by: Conor Schott, Fermin Moreno, Berent Baysal

@date
Date: 3/14/2024


@note
RAW VERSION
This version of the driver is designed to capture raw data exclusively from the MLX90640 sensor.
Calibration processes are omitted in order to conserve memory resources.
!"""


from gc import collect, mem_free
from ucollections import namedtuple
from mlx90640.regmap import (
    REGISTER_MAP,
    EEPROM_MAP,
    RegisterMap,
    CameraInterface,
    REG_SIZE,
    EEPROM_ADDRESS,
    EEPROM_SIZE,
)
# from mlx90640.calibration import CameraCalibration, TEMP_K
from mlx90640.image import RawImage, Subpage, get_pattern_by_id


class CameraDetectError(Exception):
    """Exception raised for camera detection errors."""


def detect_camera(i2c):
    """Detect the camera with the assumption that it is the only device on the
    I2C interface.

    @param i2c: The I2C interface.
    @type i2c: object
    @returns: A reference to a new MLX90640 object which has been created.
    !"""
    scan = i2c.scan()
    if len(scan) == 0:
        raise CameraDetectError("No camera detected")
    if len(scan) > 1:
        scan = ", ".join(str(s) for s in scan)
        raise CameraDetectError(f"Multiple devices on I2C bus: {scan}")
    cam_addr = scan[0]
    return MLX90640(i2c, cam_addr)


class RefreshRate:
    """Class for managing the refresh rate.!"""
    values = tuple(range(8))

    @classmethod
    def get_freq(cls, value):
        """Get frequency from the given value.!"""
        return 2.0**(value - 1)

    @classmethod
    def from_freq(cls, freq):
        """Get value from the given frequency.!"""
        _, value = min(
            (abs(freq - cls.get_freq(v)), v)
            for v in cls.values
        )
        return value

CameraState = namedtuple('CameraState',
                         ('vdd', 'ta', 'ta_r', 'gain', 'gain_cp'))


class DataNotAvailableError(Exception):
    """Exception raised when data is not available.!"""


class MLX90640:
    """Class representing the MLX90640 thermal infrared camera.!"""

    def __init__(self, i2c, addr):
        """Initialize the MLX90640 camera object.!"""
        self.iface = CameraInterface(i2c, addr)
        self.registers = RegisterMap(self.iface, REGISTER_MAP)
        self.eeprom = RegisterMap(self.iface, EEPROM_MAP, readonly=True)
        self.calib = None
        self.raw = None
        self.last_read = None


    def setup(self, *, calib=None, raw=None, image=None):
        """Setup the camera with optional calibration, raw data, and processed image.!"""
        collect()
        self.raw = raw or RawImage()
        collect()


    @property
    def refresh_rate(self):
        """Get the refresh rate."""
        return RefreshRate.get_freq(self.registers['refresh_rate'])

    @refresh_rate.setter
    def refresh_rate(self, freq):
        """Set the refresh rate.!"""
        self.registers['refresh_rate'] = RefreshRate.from_freq(freq)


    def get_pattern(self):
        """Get the read pattern."""
        return get_pattern_by_id(self.registers['read_pattern'])


    def set_pattern(self, pat):
        """Set the read pattern.!"""
        self.registers['read_pattern'] = pat.pattern_id


    def read_vdd(self):
        """Read the supply voltage.!"""
        return 0.0


    def _adc_res_corr(self):
        """Perform ADC resolution correction.!"""
        return 0


    def read_ta(self):
        """Read the ambient temperature.!"""
        return 0.0


    def read_gain(self):
        """Read the gain."""
        return float(self.registers['gain'])


    def read_state(self, *, tr=None):
        """Read the camera state."""
        gain = self.read_gain()
        cp_sp_0 = gain * self.registers['cp_sp_0']
        cp_sp_1 = gain * self.registers['cp_sp_1']

        ta = self.read_ta()

        ta_abs = ta + 25
        ta_r = (ta_abs + TEMP_K)**4
        return CameraState(
            vdd = self.read_vdd(),
            ta = ta,
            ta_r = ta_r,
            gain = gain,
            gain_cp = (cp_sp_0, cp_sp_1),
        )


    @property
    def has_data(self):
        """Check if data is available from the camera.!"""
        return bool(self.registers['data_available'])


    @property
    def last_subpage(self):
        """Get the last subpage.!"""
        return self.registers['last_subpage']


    def read_image(self, sp_id = None):
        """Read the image.!"""
        if not self.has_data:
            raise DataNotAvailableError

        if sp_id is None:
            sp_id = self.last_subpage

        subpage = Subpage(self.get_pattern(), sp_id)
        self.last_read = subpage
        self.raw.read(self.iface, subpage.sp_range())
        self.registers['data_available'] = 0
        return self.raw
