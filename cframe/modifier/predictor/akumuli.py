#!/usr/bin/env python
# coding: utf-8
"""Predictor classes."""

from cframe.backend.predictormod import CorePredictor


class Akumuli(CorePredictor):

    name = 'Akumuli'

    def __init__(self, bits=32, table_size=128, *args, **kwargs):
        if (table_size & (table_size - 1)) != 0:
            raise ValueError("`table_size` should be a power of two!")
        self._table = [0]*table_size
        self._mask = table_size - 1
        self._last_hash = 0
        self._bits = bits
        self._fff = 0xFFFFFFFF if bits == 32 else 0xFFFFFFFFFFFFFFFF
        self._ctx = 32 - 11 if bits == 32 else 64-14

    def update(self, val):
        self._table[self._last_hash] = val
        self._last_hash = self._hashfunction(val)

    def predict(self):
        return self._table[self._last_hash]

    def _hashfunction(self, val):
        shifted = (self._last_hash << 5) & self._fff
        result = (shifted ^ (val >> self._ctx)) & self._mask
        return int(result)  # TODO: Somehow a transformation to int is necessary. Why?

    def __repr__(self):
        return "{} (bits {})".format(self.name, self._bits)