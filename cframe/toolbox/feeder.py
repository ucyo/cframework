#!/usr/bin/env python
# coding: utf-8
"""
Feeder prepares the Sequence objects to be consumed by the Predictors.
"""
from cframe.backend.sequenceobj import BaseSequence  # Input
from cframe.objects.arrays.predictionarray import PredictionArray
from cframe.toolbox import get_bits, _check_input
import numpy as np


class BaseFeeder:
    """Feeder class as a common base for following feeder methods.
    """

    def __init__(self, predictor, *args, **kwargs):
        self.pred = predictor
        self.args = args
        self.kwargs = kwargs
        self.obj = 0  # Count elements predicted

    def reset(self):
        """Resetting the Predictor to initial state.

        Possibility for the Feeder entity to reset the predictor to its original initial state.
        """
        self.predictor = self.pred(*self.args, **self.kwargs)
        self.obj = 0

    def step(self, value):
        """Predicting next element and updating with actual value.
        """
        prediction = self.predictor.predict()
        self.predictor.update(value)
        self.obj += 1
        return prediction

    def feed(self, *args, **kwargs):
        raise NotImplementedError("feed() is not implemented")


class SeqFeeder(BaseFeeder):
    """Feeder for predictors using the Sequence objects for prediction."""

    def feed(self, seqobj, pa=True):
        """Feed Sequence object to initial predictors"""
        seqobj = _check_input(seqobj, BaseSequence)
        self.kwargs['bits'] = get_bits(seqobj.data)

        self.reset()
        if not pa:
            result = np.array([self.step(x) for x in seqobj.data])
        else:
            result = np.zeros_like(seqobj.data).reshape(seqobj.shape)
            for i in range(len(seqobj.sequence)):
                idx = seqobj[i]
                true = seqobj.data[i]
                prediction = self.step(true)
                result.flat[idx] = prediction
            result = PredictionArray(result)
        name = str(self.predictor)
        self.reset()
        return name, result