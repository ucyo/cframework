#!/usr/bin/env python
# coding: utf-8
"""Mapper modifier to transform FloatArray to IntegerArray."""


from cframe.backend.mappermod import BaseMapper
from cframe.objects.arrays.floatarray import FloatArray  # Input
from cframe.objects.arrays.integerarray import IntegerArray  # Output
import numpy as np
from bitstring import BitArray as ba


class Lindstrom(BaseMapper):
    """Map float to uint with saving order (based on Lindstrom et al. 2004)."""

    name = "Lindstrom"

    @staticmethod
    def map(floatarray):
        if not isinstance(floatarray, FloatArray):
            err_type = "Expected FloatArray, got {}".format(type(floatarray))
            raise TypeError(err_type)
        if floatarray.array.dtype in (np.float32,):
            length, d = 32, np.uint32
        elif floatarray.array.dtype in (np.float64, float,):
            length, d = 64, np.uint64
        else:
            err_msg = 'Expected 32 or 64 bits, got {}'.format(floatarray.array.dtype)
            raise TypeError(err_msg)
        data = _vlindstrom(floatarray.array, length).astype(d)
        return IntegerArray(data)

    @staticmethod
    def revmap(integerarray):
        if not isinstance(integerarray, IntegerArray):
            err_type = "Expected IntegerArray, got {}".format(type(integerarray))
            raise TypeError(err_type)
        if integerarray.array.dtype in (np.int32, np.uint32):
            length, d = 32, np.float32
        elif integerarray.array.dtype in (np.int64, np.uint64, int,):
            length, d = 64, np.float64
        else:
            err_msg = 'Expected 32 or 64 bits, got {}'.format(integerarray.array.dtype)
            raise TypeError(err_msg)
        data = _v_rev_lindstrom(integerarray.array, length).astype(d)
        return FloatArray.from_numpy(data)


def _rev_lindstrom(value, length):
    result = ba(uintbe=value, length=length)# ^ ba(floatbe=2, length=length)
    if result.bin[0] == "1":
        result.invert(0)
    else:
        result.invert()
    return result.floatbe
_v_rev_lindstrom = np.frompyfunc(_rev_lindstrom, 2, 1)


def _lindstrom(value, length):
    result = ba(floatbe=value, length=length)# ^ ba(floatbe=2, length=length)
    if value < 0:
        result.invert()
    else:
        result.invert(0)
    return result.uintbe
_vlindstrom = np.frompyfunc(_lindstrom, 2, 1)
