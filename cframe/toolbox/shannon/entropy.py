#!/usr/bin/env python
# coding=utf-8
"""Calculate different kind of entropy for time series.

TODO: Should the input parameters be normalised?
TODO: For floats binning should implemented


"""

from collections import Counter
from functools import partial
from cframe.toolbox.shannon import symbol as sym
import pandas as pd
import numpy as np


def main(dataarray, symbolwindow, entropy='shannon', symbol='diff', **kwargs):
    """Calculate Shannon Entropy of time series.

    Before the entropy calculation a mapping to symbols will occur.

    Arguments
    =========
    window : int
        Window size of values chosen from the series to build mapping.
    method : str
        Choose method for building mapping. Available options are:
        'diff'.
    """
    assert dataarray.squeeze().ndim == 1, "DataArray is not 1 dimensional"

    if symbol in ('diff','updown'):
        symbolmap = sym.updown(dataarray, symbolwindow)
    elif symbol in ('bin', 'binary'):
        symbolmap = sym.binary(dataarray, symbolwindow)
    else:
        symbolmap = dataarray

    if entropy in ('shannon',):
        result = _apply_method(symbolmap, _shannon, **kwargs)
    elif entropy in ('ApEn', 'approx'):
        result = _apply_method(symbolmap, _approx_entropy, **kwargs)
    elif entropy in ('SampleEn', 'sample'):
        result = _apply_method(symbolmap, _sample_entropy, **kwargs)
    else:
        raise EntropyError("Entropy method not valid.")
    return result


def _shannon(series, **kwargs):
    """Calculates the Shannon Entropy of a series."""
    probabilities, lns = Counter(series.values), float(series.size)
    return -sum(count/lns * np.log2(count/lns) for count in probabilities.values())


def _approx_entropy(series, r, m=3, **kwargs):
    """Implementation of the Approximate Entropy.

    Link
    ====
    https://en.wikipedia.org/wiki/Approximate_entropy

    Arguments
    =========
    U : np.ndarray
      Time series for which the ApEn is being calculated.
    m : int
      Rolling window length of compared subset.
    r : int
      Filtering level of distance function
    """

    def _maxdist(x_i, x_j):
        return max([abs(ua - va) for ua, va in zip(x_i, x_j)])

    def _phi(m):
        x = [[series[j] for j in range(i, i + m - 1 + 1)] for i in range(N - m + 1)]
        C = [len([1 for x_j in x if _maxdist(x_i, x_j) <= r]) / (N - m + 1.0) for x_i in x]
        return (N - m + 1.0)**(-1) * sum(np.log(C))

    N = series.size

    return abs(_phi(m) - _phi(m+1))


def _sample_entropy(series, r=None, m=2, **kwargs):
    """Implementation of the Sample Entropy.

    Link
    ====
    https://en.wikipedia.org/wiki/Sample_entropy

    Arguments
    =========
    U : np.ndarray
      Time series for which the ApEn is being calculated.
    m : int
      Rolling window length of compared subset.
    r : int
      Filtering level of distance function
    """
    if r is None:
        r = series.std() * .2

    def _maxdist(x_i, x_j):
        return max([abs(ua - va) for ua, va in zip(x_i, x_j)])

    def _phi(m):
        x = [[series[j] for j in range(i, i + m - 1 + 1)] for i in range(N - m + 1)]
        C = [(len([1 for x_j in x if _maxdist(x_i, x_j) <= r])) - 1 for x_i in x]
        return sum(C)

    N = series.size

    return np.log(_phi(m)/_phi(m+1))

class EntropyError(BaseException):
    """Base error class for entropy methods."""
    pass


def _apply_method(series, entropy_method, **kwargs):
    if isinstance(series, pd.Series):
        return entropy_method(series.dropna(), **kwargs)
    return entropy_method(pd.Series(series).dropna(), **kwargs)

shannon_diff = partial(main, symbol='diff', entropy='shannon')
shannon_binary = partial(main, symbol='binary', entropy='shannon')
sample = partial(main, symbol=None, entropy='sample')
approx = partial(main, symbol=None, entropy='approx')
