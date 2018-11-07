#!/usr/bin/env python
# coding: utf-8
"""
Toolbox with small functions for everyday use.
"""
import pkg_resources
from functools import lru_cache
import numpy as np

_datamapping = {
    'pre': pkg_resources.resource_filename('cframe', 'data/sresa1b_ncar_ccsm3-example.nc'),
}

def get_bits(data):
    if data.dtype in (np.int64, np.uint64, np.float64, int, float):
        bits = 64
    elif data.dtype in (np.int32, np.uint32, np.float32):
        bits = 32
    else:
        err = "Expected 32 or 64 Bit, got {}".format(data.dtype)
        raise TypeError(err)
    return bits

def _raiseTypeError(obj, clas):
    if not isinstance(obj, clas):
        err = "Expected {}, got {}".format(clas, type(obj))
        raise TypeError(err)
    return obj

def check_methods(C, *methods):
    """Check if C implemented *methods.

    INFO
    ====
    Source: python3.6/_collections_abc.py
    """
    mro = C.__mro__
    for method in methods:
        for B in mro:
            if method in B.__dict__:
                if B.__dict__[method] is None:
                    return NotImplemented
                break
        else:
            return NotImplemented
    return True


def get_data_path(key):
    """Get example data paths."""
    return _datamapping.get(key, False)


@lru_cache(32)
def getNAN(dtype):
    """Return NaN value based on np.dtype."""
    if not isinstance(dtype, np.dtype):
        err = "Expected np.dtype, got {}".format(type(dtype))
        raise TypeError(err)
    return np.array([np.nan]).astype(dtype)[0]


def _check_input(obj, source):
    if not isinstance(obj, source):
        err = "Expected {} object, got {}".format(source, type(obj))
        raise TypeError(err)
    return obj

