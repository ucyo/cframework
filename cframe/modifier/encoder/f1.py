#!/usr/bin/env python
# coding: utf-8
"""
Encoder for format 1.
"""

from cframe.backend.encodermod import BaseEncoder
from cframe.objects.arrays.residualarray import ResidualArray
from cframe.objects.coded import Coded
from cframe.modifier.encoder import raw
import numpy as np


class F1(BaseEncoder):

    name = "F1 Encoder"

    @staticmethod
    def encode(rarr, start, shape):
        npad, lpad, nvalues, lvalues, bits = Look.compress(rarr.array)
        nbytes = bytes(nvalues)
        lbytes = bytes(lvalues)
        return Coded(lpad, npad, lbytes, nbytes, start, bits, shape, version=1)

    @staticmethod
    def decode(coded):
        recon_rarr = Look.decompress(lpad=coded.lpad,
                                     npad=coded.npad,
                                     lvalues=list(coded.blzc),
                                     nvalues=list(coded.bnoise),
                                     bits=coded.bits)
        dtype_adjusted = np.array(recon_rarr, dtype='uint{}'.format(coded.bits))
        dtype_adjusted = dtype_adjusted.astype('int{}'.format(coded.bits))
        # shape_adjusted = dtype_adjusted.reshape(coded.shape)
        # return ResidualArray(shape_adjusted)
        return ResidualArray(dtype_adjusted)


class Look:
    """Encoding of <uint> data.

    The data is being split into Leading Zero Lengths and noise data. The LZC are transformed into

    Note
    ====
    This method will not work because of transformation errors on int32 values.
    """

    version=1

    def compact(data):
        """Compact representation of data. Needs LZC for decompression."""
        bits = int(str(data.dtype)[-2:])
        strings = "".join(raw.vget_noise(data, bits).reshape(data.size).tolist())

        pad = 8 - (len(strings) % 8)
        pad = 0 if pad == 8 else pad
        result = "0"*pad
        result += strings
        result = [int(result[i:i+8], 2) for i in range(0, len(result), 8)]
        return pad, result

    def zeros(data):
        """Compact 6 Bit representation of LZC."""
        bits = int(str(data.dtype)[-2:])
        result = raw.vleading_zeros(data, bits).astype('uint8')
        result = raw.vbinary_repr(result, 6)
        strings = "".join(result.reshape(data.size).tolist())

        pad = 8 - (len(strings) % 8)
        pad = 0 if pad == 8 else pad
        result = "0"*pad
        result += strings
        result = [int(result[i:i+8], 2) for i in range(0, len(result), 8)]
        return pad, result

    def compress(data):
        bits = int(str(data.dtype)[-2:])
        npad, nvalues = Look.compact(data)
        lpad, lvalues = Look.zeros(data)
        return npad, lpad, nvalues, lvalues, bits

    def decompress(lpad, npad, lvalues, nvalues, bits):
        lstrings = raw.vbinary_repr(lvalues, 8)
        lstrings = "".join(lstrings)[lpad:]
        lvalues = [int(x, 2) for x in Look.split(lstrings, 6)]

        nstrings = raw.vbinary_repr(nvalues, 8)
        nstrings = "".join(nstrings)[npad:]
        nvalues  = [int('0'*y+x, 2) if y and y!=bits else 0 for y,x in zip(lvalues, Look.noisypart(nstrings, lvalues, bits))]
        return nvalues

    def noisypart(test_noise_str, zeros, bits):
        i=0
        for lzc in zeros:
            yield test_noise_str[i:i+bits-lzc]
            i += bits-lzc

    def split(inp, size):
        return [inp[start:start+size] for start in range(0, len(inp), size)]


    def test(runs=30):
        run = 0
        errstates = {}
        while run < runs:
            st = np.random.get_state()
            data = np.random.randint(-2**16,2**16,10000).astype('float32').view('uint32')
            npad, lpad, nvalues, lvalues, bits = Look.compress(data)
            recon = Look.decompress(lpad, npad, lvalues, nvalues, 32)
            success = np.array_equal(recon, data)
            if not success:
                errstates.update({run: st})
            run += 1
        return errstates


if __name__ == '__main__':
    result = Look.test()
    print(result)
