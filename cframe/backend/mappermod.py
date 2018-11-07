#!/usr/bin/env python
# coding: utf-8
"""Interface for Mapper modifiers."""

from abc import ABCMeta, abstractmethod, abstractproperty
from cframe.toolbox import check_methods

class MapperInterface(metaclass=ABCMeta):
    """Modifier to transform input to an np.array of dtype int."""

    __slots__ = ()

    @abstractmethod
    def map(self):
        """Transform given np.array into a integer np.array."""
        return None

    @classmethod
    def __subclasshook__(cls, C):
        if cls is MapperInterface:
            return check_methods(C, "map")
        return NotImplemented


class BaseMapper(MapperInterface):

    @abstractproperty
    def name(self):
        return NotImplemented

    def __repr__(self):
        return str(self.name)
