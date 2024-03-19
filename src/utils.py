"""!
Struct and Field Description Utilities

This script provides utilities for working with structured data and defining field descriptions. It includes functions for creating arrays filled with a specified value, calculating two's complement, and creating field descriptions.

The `array_filled` function creates an array of a specified type and length, optionally filled with a specified value.

The `twos_complement` function calculates the two's complement of a value given its bit size.

The `field_desc` function creates a field description namedtuple based on the name, number of bits, position, and signedness of a field.

The `StructProto` class defines the layout of structured data based on field descriptions.

The `Struct` class provides methods for accessing and modifying structured data using a buffer and a predefined layout.

@author
Author:
Dr. Ridgely

Modifed by: Conor Schott, Fermin Moreno, Berent Baysal

"""

from array import array
from ucollections import namedtuple
from uctypes import (
    INT8, UINT8,
    INT16, UINT16,
    BFUINT16,
    BF_POS,
    BF_LEN,
    BIG_ENDIAN,
    addressof,
    struct as uc_struct,
)

def array_filled(typecode, length, fill=0):
    """!
    Create an array filled with a specified value.

    Args:
        typecode (str): Typecode of the array (e.g., 'H' for unsigned short).
        length (int): Length of the array.
        fill (int, optional): Value to fill the array with. Defaults to 0.

    Returns:
        array: Filled array.
    """
    return array(typecode, (fill for i in range(length)))

def twos_complement(bits, value):
    """!
    Calculate the two's complement of a value given its bit size.

    Args:
        bits (int): Number of bits.
        value (int): Value to calculate the two's complement of.

    Returns:
        int: Two's complement of the value.
    """
    if value < 0:
        return value + (1 << bits)
    if value >= (1 << (bits - 1)):
        return value - (1 << bits)
    return value

FD_BYTE = object()
FD_WORD = object()

FieldDesc = namedtuple('FieldDesc', ('name', 'layout', 'signed_bits'))
def field_desc(name, bits, pos=0, signed=False):
    """!
    Create a field description namedtuple.

    Args:
        name (str): Name of the field.
        bits (int or object): Number of bits for the field or FD_WORD/FD_BYTE for word/byte-sized fields.
        pos (int, optional): Position of the field. Defaults to 0.
        signed (bool, optional): Whether the field is signed. Defaults to False.

    Returns:
        FieldDesc: Namedtuple describing the field.
    """
    if bits is FD_WORD:
        layout = 0 | (INT16 if signed else UINT16)
        return FieldDesc(name, layout, None)
    
    if bits is FD_BYTE:
        layout = pos | (INT8 if signed else UINT8)
        return FieldDesc(name, layout, None)

    layout = 0 | BFUINT16 | pos << BF_POS | bits << BF_LEN
    return FieldDesc(name, layout, bits if signed else None)


class StructProto:
    def __init__(self, fields):
        """!
        Initialize the StructProto object.

        Args:
            fields (list of FieldDesc): List of field descriptions.
        """
        self.layout = {}
        self.signed = {}
        for fld in fields:
            self.layout[fld.name] = fld.layout
            if fld.signed_bits is not None:
                self.signed[fld.name] = fld.signed_bits

class Struct:
    def __init__(self, buf, proto):
        """!
        Initialize the Struct object.

        Args:
            buf (bytearray): Buffer containing the structured data.
            proto (StructProto): StructProto object defining the layout of the structured data.
        """
        self._signed = proto.signed
        self._struct = uc_struct(addressof(buf), proto.layout, BIG_ENDIAN)

    def __getitem__(self, name):
        """!
        Get the value of a field by name.

        Args:
            name (str): Name of the field.

        Returns:
            int: Value of the field.
        """
        value = getattr(self._struct, name)
        signed = self._signed.get(name)
        if signed is not None:
            return twos_complement(signed, value)
        return value

    def __setitem__(self, name, value):
        """!
        Set the value of a field by name.

        Args:
            name (str): Name of the field.
            value (int): Value to set.

        Returns:
            None
        """
        signed = self._signed.get(name)
        if signed is not None:
            value = twos_complement(signed, value)
        setattr(self._struct, name, value)
