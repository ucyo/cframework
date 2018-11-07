#!/usr/bin/env python
# coding: utf-8
"""Predictor classes."""

from cframe.backend.predictormod import CorePredictor


class LastValue(CorePredictor):
    """Last Value Prediction."""

    name = 'Last Value'

    def __init__(self, *args, **kwargs):
        self._prev = 0
        _, _ = args, kwargs

    def update(self, val):
        self._prev = val

    def predict(self):
        return self._prev