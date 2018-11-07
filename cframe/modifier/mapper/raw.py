#!/usr/bin/env python
# coding: utf-8
"""Mapper modifier to transform FloatArray to IntegerArray."""

import struct
from cframe.backend.mappermod import BaseMapper
from cframe.objects.arrays.floatarray import FloatArray  # Input
from cframe.objects.arrays.integerarray import IntegerArray  # Output
import numpy as np


class Raw(BaseMapper):
    """
    Raw binary mapper. Reads float binary and interprets it as integer.
    """

    name = "Raw"

    @staticmethod
    def map(floatarray):
        data = floatarray.array.view('int32').copy()
        return IntegerArray(data)

    @staticmethod
    def revmap(integerarray):
        data = integerarray.array.view('float32').copy()
        return FloatArray.from_numpy(data)
