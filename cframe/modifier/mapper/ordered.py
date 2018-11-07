#!/usr/bin/env python
# coding: utf-8
"""Mapper modifier to transform FloatArray to IntegerArray."""


from cframe.backend.mappermod import BaseMapper
from cframe.objects.arrays.floatarray import FloatArray  # Input
from cframe.objects.arrays.integerarray import IntegerArray  # Output
import numpy as np
from bitstring import BitArray as ba


class Ordered(BaseMapper):
    """Map float to int with saving order (based on Lindstrom et al. 2004)."""

    name = "Order"

    @staticmethod
    def map(floatarray):
        data = np.where(floatarray.array > 0,
                        floatarray.array.view('uint32') + 2**31,
                        ~floatarray.array.view('uint32'))
        return IntegerArray(data)

    @staticmethod
    def revmap(integerarray):
        data = np.where(integerarray.array > 2**31,
                        (integerarray.array - 2**31).astype('uint32').view('float32'),
                        (~integerarray.array).astype('uint32').view('float32'))
        # TODO Check why np.nan values are mapped to the value below
        data[data == 5.8774704e-39] = np.nan
        return FloatArray.from_numpy(data)
