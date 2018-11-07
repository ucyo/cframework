#!/usr/bin/env python
# coding: utf-8
"""Mapper modifier to transform FloatArray to IntegerArray."""

import struct
from cframe.backend.mappermod import BaseMapper
from cframe.objects.arrays.floatarray import FloatArray  # Input
from cframe.objects.arrays.integerarray import IntegerArray  # Output
import numpy as np


class RawBinary(BaseMapper):
    """
    Raw binary mapper. Reads float binary and interprets it as integer.
    """

    name = "RawBinary"

    @staticmethod
    def map(floatarray):
        if not isinstance(floatarray, FloatArray):
            err_type = "Expected FloatArray, got {}".format(type(floatarray))
            raise TypeError(err_type)
        if floatarray.array.dtype in (np.float32,):
            i, o, d = ('>f', '>l', np.int32)
        elif floatarray.array.dtype in (np.float64, float,):
            i, o, d = ('>d', '>Q', np.int64)
        else:
            err_msg = 'Expected 32 or 64 bits, got {}'.format(floatarray.array.dtype)
            raise TypeError(err_msg)
        data = _vraw(floatarray.array, i, o).astype(d)
        return IntegerArray(data)

    @staticmethod
    def revmap(integerarray):
        if not isinstance(integerarray, IntegerArray):
            err_type = "Expected IntegerArray, got {}".format(type(integerarray))
            raise TypeError(err_type)
        if integerarray.array.dtype in (np.int32, np.uint32):
            i, o, d = ('>l', '>f', np.float32)
        elif integerarray.array.dtype in (np.int64, np.uint64, int,):
            i, o, d = ('>Q', '>d', np.float64)
        else:
            err_msg = 'Expected 32 or 64 bits, got {}'.format(integerarray.array.dtype)
            raise TypeError(err_msg)
        data = _vraw(integerarray.array, i, o).astype(d)
        return FloatArray.from_numpy(data)
    

def _raw(value, itype, otype):
    s = struct.pack(itype, value)
    return struct.unpack(otype, s)[0]
_vraw = np.vectorize(_raw)