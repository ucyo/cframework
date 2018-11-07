#!/usr/bin/env python
# coding: utf-8
"""Interface for Predictor modifiers.
"""

from abc import ABCMeta, abstractmethod, abstractproperty
from cframe.toolbox import check_methods


class PredictorInterface(metaclass=ABCMeta):
    """Modifier to predict based on Information Space."""

    __slots__ = ()

    @abstractmethod
    def predict(self):
        """Prediction for each Information Context in Information Space."""
        return None

    @abstractmethod
    def update(self):
        """Prediction for each Information Context in Information Space."""
        return None

    @classmethod
    def __subclasshook__(cls, C):
        if cls is PredictorInterface:
            return check_methods(C, "predict", "update")
        return NotImplemented


class BasePredictor(PredictorInterface):

    @abstractproperty
    def name(self):
        return NotImplemented

    def __repr__(self):
        return str(self.name)


class CorePredictor(BasePredictor):
    pass


class MixedPredictor(BasePredictor):
    pass


class NDPredictor(BasePredictor):
    pass
