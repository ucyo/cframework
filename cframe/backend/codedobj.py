#!/usr/bin/env python
# coding=utf-8
"""Interface for Sequence objects."""

import os
from abc import ABCMeta, abstractproperty
from cframe.toolbox import check_methods  # , np2vtr
import numpy as np


class CodedInterface(metaclass=ABCMeta):
    """A Sequence object for prediction order.

    Attributes
    ==========
    sequence : list
        List of indices for order of prediction.
    """

    __slots__ = ()

    @abstractproperty
    def blzc(self):
        """Sequence list via indices."""
        return []

    @abstractproperty
    def bnoise(self):
        """Sequence list via indices."""
        return []

    @classmethod
    def __subclasshook__(cls, C):
        if cls is CodedInterface:
            return check_methods(C, "blzc, bnoise")
        return NotImplemented


class BaseCoded(CodedInterface):

    def __repr__(self):
        return "Coded object: Size ~{}".format(str(self.nbytes))

    def __eq__(self, other):
        if isinstance(other, BaseCoded):
            return self.blzc == other.blzc and self.bnoise == other.bnoise

    @property
    def nbytes(self):
        return len(self.blzc + self.bnoise)
