#!/usr/bin/env python
# coding: utf-8
"""
Reader for transformation of different kind of files to FloatArray with
the ability to choose subsets of the source data.
"""

import os
import xarray as xr
import numpy as np

from cframe.toolbox import get_data_path, _raiseTypeError
from cframe.objects.arrays import floatarray as fa
import lzma

class Reader:

    name = "Reader"

    @staticmethod
    def from_dataarray(dataarray):
        dataarray = _raiseTypeError(dataarray, xr.DataArray)
        dataarray = dataarray.astype(np.float32)  # TODO: Forced to do only 32 bits
        result = fa.FloatArray(dataarray.values)
        return result

    @staticmethod
    def from_dataset(dataset, var):
        dataset = _raiseTypeError(dataset, xr.Dataset)
        if not hasattr(dataset, var):
            avail = list(dataset.data_vars)
            err = "{} not in Dataset, only {}".format(var, avail)
            raise KeyError(err)
        dataarray = getattr(dataset, var)
        return Reader.from_dataarray(dataarray=dataarray)

    @staticmethod
    def from_numpy(array):
        array = _raiseTypeError(array, np.ndarray)
        if array.dtype not in (float, np.float32, np.float64):
            err = "Expected float dtype, got {}".format(array.dtype)
            raise TypeError(err)
        array = array.astype(np.float32)  # TODO: Forced to do only 32 bits
        return fa.FloatArray(array)

    @staticmethod
    def from_netcdf(filename, var, *args, **kwargs):
        if not os.path.isfile(filename):
            err = "{} is not a file.".format(filename)
            raise FileNotFoundError(err)
        ds = xr.open_dataset(filename, *args, **kwargs)
        return Reader.from_dataset(dataset=ds, var=var)

    @staticmethod
    def from_data(key, var, *args, **kwargs):
        path = get_data_path(key)
        return Reader.from_netcdf(path, var,  *args, **kwargs)