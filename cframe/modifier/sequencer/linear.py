#!/usr/bin/env python
# coding: utf-8
"""Sequencer modifier."""

from cframe.modifier.sequencer import _check_input
from cframe.backend.sequencermod import BaseSequencer
from cframe.objects.sequence import IndexSequence
import numpy as np


class Linear(BaseSequencer):
    """Linear output sequence for N dimensional arrays."""

    name = 'Linear'

    @staticmethod
    def flatten(startnode, integerarray, order=None):
        startnode, integerarray = _check_input(startnode, integerarray)
        shape = integerarray.array.shape
        tmpdata = np.arange(np.prod(shape)).reshape(shape)
        nodenames = (tmpdata + 1).astype(str)
        if not order or order in ('c', 'C'):
            new = nodenames.copy()
        elif order in ('f', 'F'):
            new = np.transpose(nodenames).copy()
        else:
            new = np.transpose(nodenames, order).copy()

        startidx = np.where(new.flat == startnode)[0][0]
        nodelist = np.roll(new.flat, -startidx)
        seq = nodelist.astype(np.int32) - 1
        data = np.array([integerarray.array.flat[x] for x in seq],
                        dtype=integerarray.array.dtype)
        return IndexSequence(seq, shape, data, order=order)
