#!/usr/bin/env python
# coding: utf-8
"""
Tests for mapper functions.
"""

from cframe.objects.arrays.floatarray import FloatArray
from cframe.modifier.mapper.lindstrom import Lindstrom
from cframe.modifier.mapper.rawbinary import RawBinary
import numpy as np
import pytest

MAPPERS = [
    Lindstrom,
    RawBinary
]

@pytest.mark.parametrize('mapper', MAPPERS)
def test_mapping_and_reverse_work(mapper):
    f = FloatArray.from_data('pre', 'tas')
    iarr = mapper.map(f)
    fnew = mapper.revmap(iarr)
    assert np.array_equal(fnew.array, f.array)