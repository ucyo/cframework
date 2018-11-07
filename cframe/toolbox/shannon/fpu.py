#!/usr/bin/env python
# coding=utf-8
"""Floating Point Unit/Uint representation."""


import numpy as np
from bitstring import BitArray as ba


class FPMapping:
    """Floating Point Unit (FPU) for floating point mapping to unsigned integer.

    Properties
    ==========
    f : bitstring.BitArray
        Floating point value to be mapped. Native 'float' values will be mapped
        to uint64.
    U : uint32, uint64
        Mapping to unsignet integer based on Lindstrom et al. (2004).
    e : int
        Mask for least significant bit of exponent.
    m : int
        Number of bits for mantissa/significand.
    s : int
        Mask for sign of floating point number.
    bits : [32, 64]
        Number of bits for floating point value.
    """

    def __init__(self, f):
        self.f = f

    @property
    def f(self):
        raise NotImplementedError

    @f.setter
    def f(self, value):
        raise NotImplementedError

    @property
    def bits(self):
        return self.f.len

    @property
    def bin(self):
        return self.f.bin

    @property
    def U(self):
        return self.f.uintbe

    @property
    def m(self):
        return 52 if self.f.len == 64 else 23

    @property
    def e(self):
        return 1 << self.m

    @property
    def s(self):
        _e = 11 if self.f.len == 64 else 8
        return self.e << _e

    def symbol(self, first=0):
        return (self.f >> (self.f.length - first)).uintbe

    def __repr__(self):
        return "FP: {} <U:{}, {}>".format(self.f, self.U, self.bits)

    def __add__(self, other):
        assert isinstance(other, FPU), "Not a FPU class."
        assert self.bits == other.bits, "Bits must be equal."

    @property
    def lzc(self):
        """Count leading zeroes."""
        cnt = 0
        for i in range(0, self.bits):
            if self.U & (1 << (self.bits - 1 - i)) != 0:
                break
            cnt += 1
        return cnt

    @property
    def tzc(self):
        """Count trailing zeroes."""
        cnt = 0
        for i in range(0, self.bits):
            if self.U & (1 << i) != 0:
                break
            cnt += 1
        return cnt


class FPUL(FPMapping):
    """Mapping from float > int, saving order and based on Lindstrom et al. (2004)."""

    def __init__(self, f):
        self.f = f

    @property
    def f(self):
        return self._ba

    @f.setter
    def f(self, value):
        assert isinstance(value, (np.float32, np.float64, float)), "Don't understand number"
        if isinstance(value, (np.float32)):
            result = ba(floatbe=value, length=32) ^ ba(floatbe=2, length=32)
        elif isinstance(value, (np.float64, float)):
            result = ba(floatbe=value, length=64) ^ ba(floatbe=2, length=64)
        bits = result.len
        if value < 0:
            result = ~result
        else:
            result = ba(uintbe=result.uintbe ^ (1<<result.len-1), length=result.len)
        self._ba = result
        self._m, self._e = (23, 8) if bits == 32 else (52, 11)
        self._f = value


class FPUT(FPMapping):
    """Trivial mapping from float > int."""

    def __init__(self, f):
        self.f = f

    @property
    def f(self):
        return self._ba

    @f.setter
    def f(self, value):
        assert isinstance(value, (np.float32, np.float64, float)), "Don't understand number"
        if isinstance(value, (np.float32)):
            result = ba(floatbe=value, length=32)
        elif isinstance(value, (np.float64, float)):
            result = ba(floatbe=value, length=64)
        bits = result.len
        self._ba = result
        self._m, self._e = (23, 8) if bits == 32 else (52, 11)
        self._f = value


def FPU(f, method='Lindstrom'):
    """Wrapper to create floating point > int mapping."""
    if method.lower() in ['lindstrom']:
        return FPUL(f)
    elif method.lower() in ['trivial']:
        return FPUT(f)
    else:
        raise FPUError("Can not understand Mapping method '{}'.".format(method)) 


class FPUError(BaseException):
    pass
