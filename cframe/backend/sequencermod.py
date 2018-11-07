#!/usr/bin/env python
# coding: utf-8
"""Interface for Sequencer modifiers."""

from abc import ABCMeta, abstractmethod, abstractproperty
from cframe.toolbox import check_methods

class SequencerInterface(metaclass=ABCMeta):
    """Modifier which traverses an np.array."""

    __slots__ = ()

    @abstractmethod
    def flatten(self):
        """Flattening given Sequence array."""
        return None

    @classmethod
    def __subclasshook__(cls, C):
        if cls is SequencerInterface:
            return check_methods(C, "flatten")
        return NotImplemented


class BaseSequencer(SequencerInterface):

    @abstractproperty
    def name(self):
        return NotImplemented

    def __repr__(self):
        return str(self.name)
