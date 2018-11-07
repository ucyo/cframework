#!/usr/bin/env python
# coding: utf-8
"""Interface for Subtractor modifiers."""

from abc import ABCMeta, abstractmethod, abstractproperty
from cframe.toolbox import check_methods

class SubtractorInterface(metaclass=ABCMeta):
    """Modifier to subtract one np.array from another."""

    __slots__ = ()

    @abstractmethod
    def subtract(self):
        """Subtract this array from another."""
        return None

    @classmethod
    def __subclasshook__(cls, C):
        if cls is SubtractorInterface:
            return check_methods(C, "subtract")
        return NotImplemented


class BaseSubstractor(SubtractorInterface):

    @abstractproperty
    def name(self):
        return NotImplemented

    def __repr__(self):
        return str(self.name)