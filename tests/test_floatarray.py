#!/usr/bin/env python
# coding: utf-8
"""Test cases for instances of array objects."""

import pytest
import numpy as np

from cframe.objects.arrays.floatarray import FloatArray

ARR = np.arange(34, dtype=np.float32)
DTYPES = [np.int32, int, "str"]
INPUTS = [2, "sdf", (324, 122), [231.1, "weq"]]


def test_importtype():
    """"Correct initialisation."""
    assert isinstance(FloatArray(ARR), FloatArray)


@pytest.mark.parametrize("form", DTYPES)
def test_raise_error(form):
    """Wrong np.dtypes of array."""
    with pytest.raises(TypeError) as err:
        FloatArray(ARR.astype(form))
    assert "Expected np.nd" in str(err)


@pytest.mark.parametrize("value", INPUTS)
def test_value_error(value):
    """Wrong input types."""
    with pytest.raises(TypeError) as err:
        FloatArray(value)
    assert "Expected np.nd" in str(err)


def test_equal_floatarray():
    """Comparison with itself."""
    assert FloatArray(ARR) == FloatArray(ARR)


def test_floatarray_with_npndarray():
    """Comparison with related values."""
    assert FloatArray(ARR) == ARR


@pytest.mark.parametrize("value", INPUTS)
def test_floatarray_with_other_object(value):
    """Comparison with arbitary types."""
    with pytest.raises(TypeError) as err:
        _ = FloatArray(ARR) == value
    assert "Comparison failed" in str(err)
