#!/usr/bin/env python
# coding=utf-8
"""Symbol representation of time series data."""


from functools import partial
from collections import Iterable
from cframe.toolbox.shannon.fpu import FPU
import numpy as np
import pandas as pd


def main(dataarray, window, method='diff', funcargs=None):
    """Symbol representation of time series data.

    Arguments
    =========
    window : int
        Window size of values chosen from the series to build mapping.
    method : str
        Choose method for building mapping. Available options are:
        'diff'.
    """
    assert dataarray.squeeze().ndim == 1, "DataArray is not 1 dimensional"
    if not isinstance(funcargs, Iterable):
        funcargs = (funcargs, )

    if method == 'diff':
        result = _apply_method(dataarray, window, up_down_to_int, funcargs)
    elif method == 'binary':
        funcargs = (window, )
        result = _apply_method(dataarray, 1, bincut, funcargs)
    else:
        raise SymbolError("No valid method.")
    return result


def _apply_method(dataarray, window, method, funcargs):
    # return dataarray.to_series()\
    return pd.Series(dataarray)\
                    .rolling(window)\
                    .apply(method, args=funcargs)\
                    .to_xarray()

def bincut(window, size, *args):
    assert len(window) == 1, 'Only Window size 1 works'
    return FPU(window[0]).symbol(size)


def up_down_to_int(window, *args):
    """Map diff between consecutive values to binary.

    Map differences of consecutive values to their binary
    representation. True for positive, False for negative.


    Arguments
    =========
    window : np.ndarray
      Array of values which will get coded to binary.
    """
    if window.size < 2:
        raise SymbolError("Window size for 'diff' must be > 1")
    binarr = ['1' if x>=0 else '0' for x in np.diff(window)]
    result = int("".join(binarr), 2)
    return int(result)

class SymbolError(BaseException):
    """Error class for method."""
    pass


updown = partial(main, method='diff')
binary = partial(main, method='binary')
