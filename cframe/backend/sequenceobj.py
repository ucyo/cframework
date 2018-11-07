#!/usr/bin/env python
# coding=utf-8
"""Interface for Sequence objects."""

import os
from abc import ABCMeta, abstractproperty
from cframe.toolbox import check_methods#, np2vtr
import numpy as np


class SequenceInterface(metaclass=ABCMeta):
    """A Sequence object for prediction order.

    Attributes
    ==========
    sequence : list
        List of indices for order of prediction.
    """

    __slots__ = ()

    @abstractproperty
    def sequence(self):
        """Sequence list via indices."""
        return []

    @abstractproperty
    def shape(self):
        """Sequence list via indices."""
        return ()

    @abstractproperty
    def data(self):
        """Sequence list via indices."""
        return []

    @classmethod
    def __subclasshook__(cls, C):
        if cls is SequenceInterface:
            return check_methods(C, "sequence", "shape", "data")
        return NotImplemented


class BaseSequence(SequenceInterface):

    def __repr__(self):
        return str(self.sequence)

    def __getitem__(self, name):
        return self.sequence[name]

    # def to_vtr(self, name, folder):
    #     assert os.path.isdir(folder), "Folder '{}' non-existent".format(folder)
    #     assert len(self.shape) == 3, "3 Dim needed."
    #     empty = np.ones(self.shape, dtype=float) * np.nan

    #     for i, k in enumerate(self.sequence):
    #         coord = np.unravel_index(k, empty.shape)
    #         empty[coord] = i
    #         np2vtr(empty, name, '{}/{}-{}'.format(folder, name, i))
