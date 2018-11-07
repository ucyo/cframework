#!/usr/bin/env python
# coding: utf-8
"""Predictor classes."""

from cframe.backend.predictormod import CorePredictor


class Stride(CorePredictor):

    name = 'Stride'

    def __init__(self, *args, **kwargs):
        self._stride = 0
        self._prev = 0
        _, _ = args, kwargs

    def update(self, val):
        self._stride = val - self._prev
        self._prev = val

    def predict(self):
        return self._prev + self._stride