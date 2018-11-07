#!/usr/bin/env python
# coding: utf-8
"""Sequence Object for traversal direction."""

from cframe.backend.sequenceobj import BaseSequence
from cframe.toolbox import getNAN
import numpy as np


class Sequence(BaseSequence):

    def __init__(self, seq, shape, data, **kwargs):
        self.sequence = seq
        self.shape = shape
        self.data = data
        self.kwargs = kwargs

    def _get_sequence(self):
        return self._sequence
    def _set_sequence(self, value):
        if isinstance(value, str):
            err_msg = "String not allowed."
            raise TypeError(err_msg)
        value = np.array(value)
        if not (isinstance(value, np.ndarray) and value.ndim == 1):
            err_msg = "Not a numpy array with one dimension."
            raise TypeError(err_msg)
        self._sequence = value
    sequence = property(_get_sequence, _set_sequence)

    def _get_shape(self):
        return self._shape
    def _set_shape(self, value):
        if not isinstance(value, tuple):
            err = "Expected tuple, got {}.".format(type(value))
            raise TypeError(err)
        if not all([isinstance(x, int) for x in value]):
            err = "Expected ints in shape."
            raise ValueError(err)
        self._shape = value
    shape = property(_get_shape, _set_shape)

    def _get_data(self):
        return self._data
    def _set_data(self, value):
        if not isinstance(value, np.ndarray):
            err = "Expected data to be ndarray, got {}".format(type(value))
            raise TypeError(err)
        if value.size != self.sequence.size:
            err = "Sequence size ({}) " \
            "must match value size ({})".format(self.sequence.size,
                                                value.size)
        self._data = value
    data = property(_get_data, _set_data)

    @property
    def dtype(self):
        return self.data.dtype

    @property
    def nan(self):
        return getNAN(self.dtype)


class IndexSequence(Sequence):
    """Sequence object with just integer values (representing indices)."""
    name = "IndexSequence"

    def _get_sequence(self):
        return self._sequence
    def _set_sequence(self, value):
        value = np.array(value)
        if not (isinstance(value, np.ndarray) and value.ndim == 1 and
                value.dtype in (int, np.int32, np.int64)):
            err_msg = "Not a numpy array with one dimension and dtype=int."
            raise TypeError(err_msg)
        self._sequence = value
    sequence = property(_get_sequence, _set_sequence)