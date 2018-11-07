#!/usr/bin/env python
# coding: utf-8
"""Interface for Encoder modifiers."""

from abc import ABCMeta, abstractmethod, abstractproperty
from cframe.toolbox import check_methods

class EncoderInterface(metaclass=ABCMeta):
    """Modifier to encode residual array."""

    __slots__ = ()

    @abstractmethod
    def encode(self):
        """Encode residual array."""
        return None

    @abstractmethod
    def decode(self):
        """Decode encoded object."""
        return None

    @classmethod
    def __subclasshook__(cls, C):
        if cls is EncoderInterface:
            return check_methods(C, "encode", "decode")
        return NotImplemented


class BaseEncoder(EncoderInterface):

    @abstractproperty
    def name(self):
        return NotImplemented

    def __repr__(self):
        return str(self.name)