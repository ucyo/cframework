#!/usr/bin/env python
# coding: utf-8
"""Raw Encoder."""

# TODO: Must be merged with F1

from cframe.backend.encodermod import BaseEncoder
from cframe.objects.coded import Coded
from cframe.objects.arrays.residualarray import ResidualArray
from cframe.toolbox import get_bits
from functools import namedtuple
import numpy as np


def _single_leading_zeros(value, bits):
    """Leading Zero Count INCL. the last 1 bit."""
    result = np.binary_repr(value, bits)
    pos = result.find('1')
    pos = bits if pos == -1 else pos
    return pos


vleading_zeros = np.frompyfunc(_single_leading_zeros, 2, 1)


def _intlist(strs):
    """
    Transform string of 0 and 1 to list of integer.
    """
    chunks, chunk_size = len(strs), 8
    for i in range(0, chunks, chunk_size):
        sub = strs[i:i + chunk_size]
        yield int(sub, 2)


def _lzc_part(rarr):
    """Extract leading zero count of the residualarray (not compressed).
    """
    bits = get_bits(rarr.array)
    binarylz = bytes([x for x in vleading_zeros(rarr.array, bits).flat])
    pad, result = _fivebitlz(binarylz)
    return pad, result


def _fivebitlz(binarylz):
    arr = [x for x in list(binarylz)]
    fullstr = "".join([np.binary_repr(x, 5) for x in arr])
    pad = 8 - (len(fullstr) % 8)
    if pad == 8:
        pad = 0
    paddedbits = '0' * pad + fullstr
    result = bytes([x for x in _intlist(paddedbits)])
    return pad, result


def _eightbitlz(fivebitslz, pad):
    strings = "".join([np.binary_repr(x, 8) for x in list(fivebitslz[pad:])])
    result = [int(strings[i:i + 5], 2) for i in range(0, len(strings), 5)]
    result = [z for z in result]
    return result


def _noise_part(rarr):
    """
    Unpredicted part of the residualarray concatenated and beginning padded with 0s.
    """
    bits = get_bits(rarr.array)
    res = vget_noise(rarr.array, bits)
    fullstr = "".join([str(x) for x in res.flat])
    pad = 8 - (len(fullstr) % 8)
    if pad == 8:
        pad = 0
    paddedbits = '0' * pad + fullstr
    result = bytes([x for x in _intlist(paddedbits)])
    return pad, result


def _single_get_noise(value, bits):
    """Extract unpredicted part of the value from predictor EXCL. first bit."""
    binar = np.binary_repr(value, bits)
    pos = binar.find('1')
    if pos == -1:
        return ""
    else:
        return binar[pos:]


vget_noise = np.frompyfunc(_single_get_noise, 2, 1)
vbinary_repr = np.frompyfunc(np.binary_repr, 2, 1)


def _extractnoise(pad, lzc, noise, bits):
    noise = noise[pad:]
    for lzclength in lzc:
        noiselength = bits - lzclength
        if noiselength == 0:
            result = 0
        else:
            z = '0' * (lzclength) + '1'
            n = noise[:noiselength + 1]
            noise = noise[noiselength:]
            if int(z) == '1' and int(n) == 0:
                result = 0
            else:
                result = int(z + n, 2)
        yield result


class RawEncoder(BaseEncoder):

    name = 'RawEncoder'

    @staticmethod
    def encode(rarr, start, shape):
        npad, bnoise = _noise_part(rarr)
        lpad, blzc = _lzc_part(rarr)
        bits = get_bits(rarr.array)
        return Coded(lpad, npad, blzc, bnoise, start, bits, shape, version=1)

    @staticmethod
    def decode(coded):
        if not isinstance(coded, Coded):
            msg = "Expected 'coded' object, got {}".format(type(coded))
            raise TypeError(msg)
        lzc = _eightbitlz(coded.blzc, coded.lpad)
        noise = vbinary_repr(np.array(list(coded.bnoise)), 8)
        noise_string = "".join([x for x in noise])
        # return noise_string
        reconstruct_residue = [x for x in _extractnoise(coded.npad, lzc, noise_string, coded.bits)]
        reconstruct_residue = np.array(reconstruct_residue).reshape(coded.shape)
        return ResidualArray(reconstruct_residue)
