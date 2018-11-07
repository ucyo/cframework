#!/usr/bin/env python
# coding: utf-8
"""Coded object ready to be written on disk."""

from cframe.backend.codedobj import BaseCoded

class Coded(BaseCoded):

    def __init__(self, lpad, npad, blzc, bnoise, start, bits, shape, version):
        self._npad = npad
        self._lpad = lpad
        self._blzc = blzc
        self._bnoise = bnoise
        self._start = start
        self._bits = bits
        self._shape = shape
        self._version = version

    @property
    def lpad(self):
        return self._lpad

    @property
    def npad(self):
        return self._npad

    @property
    def version(self):
        return self._version

    @property
    def blzc(self):
        return self._blzc
    
    @property
    def bnoise(self):
        return self._bnoise
    
    @property
    def start(self):
        return self._start

    @property
    def bits(self):
        return self._bits
    
    @property
    def shape(self):
        return self._shape