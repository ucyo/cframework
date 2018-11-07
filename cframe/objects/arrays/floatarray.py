#!/usr/bin/env python
# coding: utf-8
"""Classes of Float Arrays."""

import numpy as np

from cframe.backend.arrayobj import BaseArray
from cframe.toolbox.reader import Reader

class FloatArray(BaseArray):
    """Basic Float Array format.
    """

    def __init__(self, arr):
        self.array = arr

    @property
    def valid_dtypes(self):
        return (np.float, np.float32, np.float64)

    @staticmethod
    def from_numpy(array):
        return Reader.from_numpy(array)

    @staticmethod
    def from_dataarray(dataarray):
        return Reader.from_dataarray(dataarray)

    @staticmethod
    def from_dataset(dataset, var):
        return Reader.from_dataset(dataset, var)

    @staticmethod
    def from_netcdf(filename, var, *args, **kwargs):
        return Reader.from_netcdf(filename, var, *args, **kwargs)

    @staticmethod
    def from_data(key, var, *args, **kwargs):
        return Reader.from_data(key, var, *args, **kwargs)
