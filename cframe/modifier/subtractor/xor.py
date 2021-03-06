#!/usr/bin/env python
# coding: utf-8
"""Subtractor modifier."""

import numpy as np
from cframe.backend.subtractormod import BaseSubstractor
from cframe.objects.arrays.residualarray import ResidualArray as RA
from cframe.objects.arrays.predictionarray import PredictionArray as PA
from cframe.objects.arrays.integerarray import IntegerArray as IA
from cframe.toolbox import _check_input


class XOR(BaseSubstractor):

    name = "XOR Subtractor"

    @staticmethod
    def subtract(predictionarray, integerarray):
        predictionarray = _check_input(predictionarray, PA)
        integerarray = _check_input(integerarray, IA)
        result = np.bitwise_xor(predictionarray.array, integerarray.array)
        return RA(result)

    @staticmethod
    def _single(one, other):
        return np.bitwise_xor(one, other)