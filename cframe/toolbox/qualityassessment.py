#!/usr/bin/env python
# coding: utf-8
"""
Quality assessment of the residue array given as input.
"""

from cframe.toolbox import get_bits
import tempfile
import numpy as np
import subprocess as sp
import os

def _trailing_zero_count(val, bits=32):
    """Count trailing zeroes."""
    cnt = 0
    for i in range(0, bits):
        if val & (1 << i) != 0:
            break
        cnt += 1
    return cnt
_vtzc = np.frompyfunc(_trailing_zero_count, 2, 1)


def _leading_zero_count(val, bits=32):
    """Count leading zeroes."""
    cnt = 0
    for i in range(0, bits):
        if val & (1 << (bits - 1 - i)) != 0:
            break
        cnt += 1
    return cnt
_vlzc = np.frompyfunc(_leading_zero_count, 2, 1)

def xz_compression(arr):
    # TODO Might be added to a separate module in the toolbox
    with tempfile.NamedTemporaryFile('wb') as f:
        name = f.name
        f.write(arr)
        sp.call(['xz','-fk9e',name])
        xz_size = os.stat(name+'.xz').st_size
        os.remove(name+'.xz')
    return xz_size

class QA(object):
    """Quality assessment (QA) of residue arrays."""
    
    @staticmethod
    def residue_report(residuearray):
        bits = get_bits(residuearray.array)
        lzc = _vlzc(residuearray.array, bits)
        tzc = _vtzc(residuearray.array, bits)
        nbits = residuearray.size * bits

        information = {
            "Bits": bits,
            "Filesize [bits]": nbits,
            "Total LZC+1" : lzc.sum() + residuearray.size,
            "Total TZC+1" : tzc.sum() + residuearray.size,
            "LZC+1 %": (lzc.sum() + residuearray.size) / nbits,
            "TZC+1 %": (tzc.sum() + residuearray.size) / nbits,
        }

        return information

    @staticmethod
    def origin_report(floatingarray):
        bits = get_bits(floatingarray.array)

        information = {
            "Bits": bits,
            "Filesize [bytes]": floatingarray.nbytes,
            "Datatype": str(floatingarray.dtype),
            "Size": floatingarray.size,
        }

        return information