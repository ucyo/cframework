#!/usr/bin/env python
# coding: utf-8
"""Sequencer modifier."""

from cframe.objects.arrays.integerarray import IntegerArray


def _check_input(startnode, integerarray):
    if not isinstance(integerarray, IntegerArray):
        err_msg = "Expected IntegerArray, got {}".format(type(integerarray))
        raise TypeError(err_msg)
    if isinstance(startnode, int):
        startnode = str(startnode + 1)  # Node was given as 'idx'
    return startnode, integerarray