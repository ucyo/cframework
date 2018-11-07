#!/usr/bin/env python
# coding: utf-8
"""Tests for Sequence objects."""

from cframe.objects.sequence import Sequence
import numpy as np
import pytest


ALLOWED = [
    [2, 3, 5, 7, ],
    (2, 4, 2, 2, 4, ),
    np.arange(52),
]

NOTALLOWED = [
    np.arange(64).reshape(8, 8)
]

NOTALLOWED_NESTING = [
    [2, 4, 652, 2, 423, [2, 5, 32, 2]]
]


@pytest.mark.parametrize('iobj', ALLOWED)
def test_valid_input(iobj):
    iobj = np.array(iobj)
    vals = iobj + np.random.randint(3, 100)
    seq = Sequence(iobj, iobj.shape, vals)
    assert all(seq.sequence == iobj)


@pytest.mark.parametrize('iobj', NOTALLOWED)
def test_invalid_input(iobj):
    with pytest.raises(TypeError) as err:
        iobj = np.array(iobj)
        vals = iobj + np.random.randint(3, 100)
        _ = Sequence(iobj, iobj.shape, vals)
    assert "Not a numpy array with one" in str(err)


@pytest.mark.parametrize('iobj', NOTALLOWED_NESTING)
def test_invalid_nesting_input(iobj):
    with pytest.raises(ValueError) as err:
        iobj = np.array(iobj)
        vals = iobj + np.random.randint(3, 100)
        _ = Sequence(iobj, iobj.shape, vals)
    assert "setting an array element with a seq" in str(err)


def test_invalid_string_input():
    with pytest.raises(TypeError) as err:
        _ = Sequence("iobj", "sdf", "sdf")
    assert "String not" in str(err)
