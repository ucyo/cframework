#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Interface for Array objects."""

from abc import ABCMeta, abstractproperty
from cframe.toolbox import check_methods
import numpy as np
import xarray as xr


class ArrayInterface(metaclass=ABCMeta):
    """Objects which consist of a single np.array.

    Attributes
    ==========
    array : np.ndarray
        Array to be accessed.
    """

    __slots__ = ()

    @abstractproperty
    def array(self):
        """Numpy array which is being accessed."""
        return None

    @classmethod
    def __subclasshook__(cls, C):
        if cls is ArrayInterface:
            return check_methods(C, "array")
        return NotImplemented


class BaseArray(ArrayInterface):
    """A class for defining common functions of Array Objects."""

    def __getattr__(self, name):
        return getattr(self.array, name)

    @abstractproperty
    def valid_dtypes(self):
        return NotImplemented

    def _get_array(self):
        return self._array
    def _set_array(self, value):
        if isinstance(value, xr.DataArray):
            value = value.values
        if hasattr(value, 'dtype') and value.dtype in self.valid_dtypes:
            self._array = value
        else:
            err_type = "Expected np.ndarray with" \
                       " {}, got {}.".format(self.valid_dtypes, type(value))
            raise TypeError(err_type)
    array = property(_get_array, _set_array)

    def __eq__(self, other):
        if isinstance(other, ArrayInterface):
            _ = np.testing.assert_array_equal(self.array, other.array)
            return True
        elif isinstance(other, np.ndarray):
            _ = np.testing.assert_array_equal(self.array, other)
            return True
        else:
            err_msg = "Comparison failed with type {}.".format(type(other))
            raise TypeError(err_msg)
