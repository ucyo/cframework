#!/usr/bin/env python
# coding: utf-8
"""Predictor classes."""

from cframe.backend.predictormod import CorePredictor

class TwoStride(CorePredictor):

    name = 'Stride (2)'

    def __init__(self, *args, **kwargs):
        self._bestStride = 0
        self._lastStride = 0
        self._prev = 0
        _, _ = args, kwargs

    def update(self, val):
        new_stride = val - self._prev
        if abs(new_stride - self._lastStride) < abs(new_stride - self._bestStride):
            self._bestStride = new_stride
        self._lastStride = new_stride

    def predict(self):
        return self._prev + self._bestStride