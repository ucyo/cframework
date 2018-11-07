#!/usr/bin/env python
# coding=utf-8
"""Building block for defining hashing functions.

These hashing functions can be build using different
atomic building blocks called Select, Fold, Shift, Xor. If no
input is given the methods fall back to a default mode
which is configured to just pass along the value.
"""

from collections import Iterable


class BaseContext:
    """Base class for atomic building blocks of context functions.

    Attributes
    ==========
    sym : '>' or '<'
        Arrows for deciding which first n binary to use. Either the
        left ('<') or right ('>') part will be taken.
    length : int
        Length of binary string to consider.
    bits : 32 or 64
        Binary length
    mode : string
        Information about the mode being used.
    """

    def __init__(self, mode=None, bits=32):
        if not mode:
            self.sym, self.length = self.default(bits)
        else:
            self.sym, self.length = self._checkCtxFunctionMode(mode, bits)
        self.bits = bits
        self.mode = mode

    @staticmethod
    def _checkCtxFunctionMode(mode, bits):
        assert mode, "There was no mode."
        assert bits in [32, 64], "Wrong bits."
        assert isinstance(mode, str), "Mode not a string."
        assert len(mode) <= 3, "Mode not less then 3 characters."
        assert mode[0] in ['>', '<'], "Mode first character not '<' or '>'."
        try:
            s, b = mode[0], int(mode[1:])
            message = "Second term not compliant with #Bits."
            assert b >= 0 and b <= bits, message
        except ValueError:
            raise ValueError("Expected numerical for second term in mode.")
        return s, b

    @staticmethod
    def default(bits):
        raise NotImplementedError("Not implemented!")

    def __repr__(self):
        return "{sym}{length}:{bits}".format(**self.__dict__)


class Select(BaseContext):
    """Atomic building block for context method: Select.

    Example
    =======
    '>6' : Choose last 6 Bits

    """

    @staticmethod
    def default(bits):
        assert bits in [32, 64], "Wrong bits."
        return '>', bits

    def __call__(self, num):
        # LOGG.info("%s of %s", self, bin(num))
        if self.sym == ">":
            part = (1 << self.length) - 1
            result = part & num
        elif self.sym == "<":
            result = int(bin(num)[2:self.length], 2)
        # LOGG.info("%s of %s = %s", self, num, result)
        return result


class Fold(BaseContext):
    """Atomic building block for context method: Fold.

    Example
    =======
    '>5' : Fold binaries of length 5 starting with the last 5 bits
        '10101001' will be '101 01001' and then '011000'

    """

    @staticmethod
    def default(bits):
        assert bits in [32, 64], "Wrong bits."
        return '>', bits

    def __call__(self, num):
        binary = bin(num)[2:]
        if self.sym == "<":
            tmp = [binary[i:i+self.length]
                   for i in range(len(binary))][::self.length]
        else:
            tmp = [binary[::-1][i:i+self.length][::-1]
                   for i in range(len(binary))][::self.length]
        splits = [x for x in tmp if x]
        return self._xor(splits)

    def _xor(self, arr):
        if len(arr) == 1:
            return int(arr[0], 2)
        return int(arr[-1], 2) ^ self._xor(arr[:-1])


class Shift(BaseContext):
    """Atomic building block for context method: Shift.

    Example
    =======
    '>6' : Shift binary 6 bits to the right (basically >> 6)

    """

    @staticmethod
    def default(bits):
        assert bits in [32, 64], "Wrong bits."
        return '>', 0

    def __call__(self, num):
        if self.sym == '<':
            return num << self.length
        return num >> self.length


class Xor:
    """Atomic building block for context method: Xor.

    Return xor result of each element in the array together.

    """

    def __call__(self, arr):
        x = Xor()
        if len(arr) != 1:
            return arr[0] ^ x(arr[1:])
        return arr[0]


class Split(BaseContext):
    """Atomic building block for context method: Split.

    Example
    =======
    '>6' : Split binary representation with right part
        having 6 bits and the other part all the left binaries.

    """

    @staticmethod
    def default(bits):
        assert bits in [32, 64], "Wrong bits."
        return '<', 0

    def __call__(self, num):
        complSym = '>' if self.sym == '<' else '<'
        binlength = len(bin(num)[2:])
        complLen = binlength - self.length
        if complLen < 0:
            complLen = 0
        complMod = complSym+str(complLen)
        if self.sym == '>':
            return Select(complMod)(num), Select(self.mode)(num)
        else:
            return Select(self.mode)(num), Select(complMod)(num)


class ContextHash:
    """ Main factory class for building hashing functions.
    """

    def __init__(self, R=None, F=None, S=None, L=None, bits=32):
        """

        The length of methods defines the order of the Context.

        Arguments
        =========
        R : iterable of modes for 'Select'
            List of Select modes to be used
        F : iterable of modes for 'Fold'
            List of Fold modes to be used
        S : iterable of modes for 'Shift'
            List of Shift modes to be used
        L : iterable of modes for 'Select'
            Last select module of the hash function
        bits : int
            Bit length
        """
        assert self._check(R, F, S), "Sizes don't fit."
        self.R = [Select(x, bits) for x in R] if R else [None]*self.ctx
        self.F = [Fold(x, bits) for x in F] if F else [None]*self.ctx
        self.S = [Shift(x, bits) for x in S] if S else [None]*self.ctx
        self.L = Select(L)
        self.bits = bits

    def __repr__(self):
        return ("Context: {ctx}\nSelect:\t{R}" +
                "\nFold:\t{F}\nShift:\t{S}\n").format(**self.__dict__)

    def _check(self, R, F, S):
        ctx = [len(x) for x in [R, F, S] if x]
        self.ctx = ctx[0] if ctx else 1
        return all([ctx[0] == x for x in ctx])

    def __call__(self, history):
        assert isinstance(history, Iterable), "History not iterable"
        if len(history) != len([x for x in history if x]):
            return None
        assert len(history) == self.ctx, "History not same length as context."
        x, res = Xor(), []
        for i, v in enumerate(history):
            tmp = self.R[i](v)
            tmp = self.F[i](tmp)
            tmp = self.S[i](tmp)
            res.append(tmp)
        return self.L(x(res))
