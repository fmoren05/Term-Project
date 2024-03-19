"""!
@file image.py
@brief Contains image storage and processing classes for the MLX90640 camera driver.

@details
This module provides classes for storing and processing images captured by the MLX90640 thermal infrared camera driver.

RAW VERSION
This version is a stripped-down MLX90640 driver that produces only raw data, not calibrated data, in order to save memory.

@author
Author:
Dr. Ridgely

Modifed by: Conor Schott, Fermin Moreno, Berent Baysal



@date
Date: 3/14/2024

"""

import math
import struct
from array import array
from ucollections import namedtuple
from mlx90640.utils import Struct, StructProto, field_desc, array_filled
from mlx90640.regmap import REG_SIZE
from mlx90640.calibration import NUM_COLS, IMAGE_SIZE, TEMP_K

PIX_STRUCT_FMT = '>h'
PIX_DATA_ADDRESS = const(0x0400)

class _BasePattern:
    """!
    Base class for pattern handling.
    """
    @classmethod
    def sp_range(cls, sp_id):
        """!
        Get the subpage range for a given subpage ID.
        @param sp_id: Subpage ID.
        @return: Generator yielding indices belonging to the given subpage.
        """
        return (idx for idx, sp in enumerate(cls.iter_sp()) if sp == sp_id)

    @classmethod
    def iter_sp(cls):
        """!
        Iterate through all subpages.
        @return: Iterator yielding subpage values.
        """
        return (cls.get_sp(idx) for idx in range(IMAGE_SIZE))

class ChessPattern(_BasePattern):
    """!
    Chess pattern class.
    """
    pattern_id = 0x1

    @classmethod
    def get_sp(cls, idx):
        """!
        Get subpage value for a given index.
        @param idx: Index.
        @return: Subpage value.
        """
        return (idx // 32 - (idx // 64) * 2) ^ (idx - (idx // 2) * 2)

class InterleavedPattern(_BasePattern):
    """!
    Interleaved pattern class.
    """
    pattern_id = 0x0

    @classmethod
    def get_sp(cls, idx):
        """!
        Get subpage value for a given index.
        @param idx: Index.
        @return: Subpage value.
        """
        return idx // 32 - (idx // 64) * 2

_READ_PATTERNS = {pat.pattern_id: pat for pat in (ChessPattern, InterleavedPattern)}

def get_pattern_by_id(pattern_id):
    """!
    Get pattern by ID.
    @param pattern_id: Pattern ID.
    @return: Pattern object.
    """
    return _READ_PATTERNS.get(pattern_id)

class Subpage:
    """!
    Subpage class.
    """
    def __init__(self, pattern, sp_id):
        """!
        Initialize Subpage object.
        @param pattern: Pattern object.
        @param sp_id: Subpage ID.
        """
        self.pattern = pattern
        self.id = sp_id

    def sp_range(self):
        """!
        Get the subpage range.
        @return: Generator yielding indices belonging to the subpage.
        """
        return self.pattern.sp_range(self.id)

class RawImage:
    """!
    Raw image class.
    """
    def __init__(self):
        """!
        Initialize RawImage object.
        """
        self.pix = array_filled('h', IMAGE_SIZE)

    def __getitem__(self, idx):
        """!
        Get item by index.
        @param idx: Index.
        @return: Item value.
        """
        return self.pix[idx]

    def read(self, iface, update_idx=None):
        """!
        Read image data.
        @param iface: Interface object.
        @param update_idx: Indices to update.
        """
        buf = bytearray(REG_SIZE)
        update_idx = update_idx or range(IMAGE_SIZE)
        for offset in update_idx:
            iface.read_into(PIX_DATA_ADDRESS + offset, buf)
            self.pix[offset] = struct.unpack(PIX_STRUCT_FMT, buf)[0]

ImageLimits = namedtuple('ScaleLimits', ('min_h', 'max_h', 'min_idx', 'max_idx'))

_INTERP_NEIGHBOURS = tuple(
    row * NUM_COLS + col
    for row in (-1, 0, 1)
    for col in (-1, 0, 1)
    if row != 0 or col != 0
)
