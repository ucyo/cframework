#!/usr/bin/env python
# coding: utf-8
""""
Tests for toolbox.
"""

import pytest
import numpy as np
from cframe import toolbox

FAIL_DTYPES = [np.uint8, np.uint16, np.int8]

@pytest.mark.parametrize('dtype', FAIL_DTYPES)
def test_get_bits_fail(dtype):
    with pytest.raises(TypeError) as err:
        data = np.arange(0, 3, 1, dtype)
        _ = toolbox.get_bits(data)

CORRECT_BITS = [
    (32, np.uint32),
    (64, np.uint64),
    (32, np.int32),
    (64, np.int64),
]

@pytest.mark.parametrize('expected, dtype', CORRECT_BITS)
def test_get_bits_pass(dtype, expected):
    data = np.arange(0, 3, 1, dtype)
    result = toolbox.get_bits(data)
    assert result == expected