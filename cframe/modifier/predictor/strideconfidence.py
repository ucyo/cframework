#!/usr/bin/env python
# coding: utf-8
"""Predictor classes."""

from functools import partial
from cframe.backend.predictormod import CorePredictor
from cframe.modifier.predictor.__context import Select


class StrideConfidence(CorePredictor):

    name = 'Stride Conf.'

    def __init__(self, threshold, *args, **kwargs):
        self._confidence = 0
        self._stride = 0
        self._prev = 0
        self._select = Select('<11')
        self._threshold = threshold
        _, _ = args, kwargs

    def update(self, val):
        trueStride = val - self._prev
        self._updateConfidence(trueStride)
        self._confidence = max(0, self._confidence)  # do not allow neg. values
        if self._confidence < self._threshold:
            self._stride = trueStride

    def _updateConfidence(self, trueStride):
        if self._select(trueStride) == self._select(self._stride):
            self._confidence += 1
        else:
            self._confidence -= 2

    def predict(self):
        return self._prev + self._stride

    def __repr__(self):
        return "{} (threshold: {})".format(self.name, self._threshold)

StrideConfidence7 = partial(StrideConfidence, threshold=7)