#!/usr/bin/env python
# coding: utf-8
"""Classes of Residual Arrays."""

import numpy as np
from cframe.backend.arrayobj import BaseArray


class ResidualArray(BaseArray):
    """Basic Residual Array format.
    """

    def __init__(self, arr):
        self.array = arr

    @property
    def valid_dtypes(self):
        return (np.int32, np.int64, int, np.uint32, np.uint64)
