#!/usr/bin/env python
# coding=utf-8
"""Create a pasc formatted compressed binary file."""

from sys import byteorder
from functools import namedtuple as nt
import numpy as np
from cframe.objects.coded import Coded


HEADER = nt('header', 'magic, version, ndim, shape, nvars, offset')
INFOFLAG = nt('iflag', 'startvalue, is_32, little_endian')
PADFLAG = nt('pflag', 'lzcpad, noisepad')
STREAM = nt('stream', 'is_32, startvalue, npad, lpad, blzc, bnoise, next_stream')


class Format:

    def to_bytes(coded):
        """
        Encode coded objects to bytes for disk output.

        This method converts the coded objects into pasc dataformat and back.

        Arguments
        =========
        coded : (list of) coded object
            Coded objects to be encoded.
        version : int
            Version of format to be encoded to.

        Returns
        =======
        result : bytes
            Pasc formatted bytes object.
        """
        if isinstance(coded, Coded):
            shape = coded.shape
            nvars = 1
            coded = [coded]
        elif isinstance(coded, list) and all([isinstance(x, Coded) and x.shape == coded[0].shape for x in coded]):
            shape = coded[0].shape
            nvars = len(coded)
        else:
            msg = "Error with input data"
            raise TypeError(msg)
        header = Format.generate_header(coded[0], nvars)
        stream = b''
        for code in coded:
            stream += Format.generate_stream(code)
        return header + stream

    def from_bytes(byte):
        """
        Decode bytes to coded objects.

        Arguments
        =========
        byte : bytes
            Pasc formatted bytes object.

        Result
        ======
        result : Coded
            Decoded Coded object from bytes.
        """
        header = Format.read_header(byte)
        nvars = header.nvars

        data = []
        byte = byte[header[-1] + 1:]
        while nvars > 0:
            pack = Format.read_stream(byte)
            data.append(pack)
            byte = byte[pack.next_stream:]
            nvars -= 1

        result = []
        for pack in data:
            bits = 32 if pack.is_32 else 64
            unpacked = Coded(pack.lpad, pack.npad, pack.blzc, pack.bnoise,
                             pack.startvalue, bits, header.shape, version=header.version)
            result.append(unpacked)
        return result if len(result) > 1 else result[0]

    def generate_header(coded, nvars):
        """
        Write metadata about the file into the header (according to pasc data format).

        Arguments
        =========
        shape : tuple
            Shape of the array to be compressed.
        nvars : int
            Number of variables to be compressed.
        version : int
            Version of pasc format to be compressed to.

        Returns
        =======
        result : bytes
            Bytes coded header information (according to pasc data format).
        """

        magic = "PSC{}".format(coded.version).encode('UTF-8')  # , **kwargs)
        ndims = np.array(len(coded.shape), np.uint8).tobytes()
        lengths = np.array(coded.shape, np.uint32).tobytes()
        nvars = np.array(nvars, np.uint8).tobytes()

        return magic + ndims + lengths + nvars

    def read_header(byte):
        """
        Read metadata about the data on disk from the header (according to pasc data format).

        Arguments
        =========
        byte : bytes
            Bytes to be read and decoded to header (according to pasc data format)

        Returns
        =======
        result : Header
            Header object of file defined by the constant HEADER.
        """
        magic = byte[:4].decode('UTF-8')
        version = int(magic[-1])
        ndims = int(byte[4])
        shape = tuple(np.frombuffer(byte[5:5 + ndims * 4], dtype=np.uint32))
        nvars = int(byte[5 + ndims * 4])
        offset = 5 + ndims * 4

        result = HEADER(magic='PSC', shape=shape, ndim=ndims,
                        nvars=nvars, version=version, offset=offset)
        return result

    def generate_infoflag(coded):
        """
        Flag byte object to be written on disk infront of data bytes (according to pasc data format).

        The flag bytes defined in the pasc data format are being generated.

        Arguments
        =========
        coded : Coded
            Coded object to be analysed and encoded.

        Returns
        =======
        result : bytes
           Flags for coded object.
        """

        flag = 0
        if byteorder == 'little':
            flag = flag + (1 << 5)
        if coded.start == 0:
            flag = flag + (1 << 6)
        if coded.bits == 32:
            flag = flag + (1 << 7)
        return bytes([flag])

    def read_infoflag(byte):
        """
        Decodes flag information (according to pasc data format).

        Arguments
        =========
        num : int
            Flag information encoded (according to pasc data format).

        Returns
        =======
        result : Flag
          Flags information about the data (according to pasc data format).
        """
        num = list(byte)[0]
        little = bool(num & (1 << 5))
        start0 = bool(num & (1 << 6))
        is32 = bool(num & (1 << 7))

        return INFOFLAG(startvalue=start0, is_32=is32, little_endian=little)

    def generate_padflag(coded):
        """
        Flag byte object to be written on disk infront of data bytes (according to pasc data format).

        The flag bytes defined in the pasc data format are being generated.

        Arguments
        =========
        coded : Coded
            Coded object to be analysed and encoded.

        Returns
        =======
        result : bytes
           Flags for coded object.
        """

        flag = coded.npad
        flag += coded.lpad << 5
        return bytes([flag])

    def read_padflag(byte):
        """
        Decodes flag information (according to pasc data format).

        Arguments
        =========
        num : int
            Flag information encoded (according to pasc data format).

        Returns
        =======
        result : Flag
          Flags information about the data (according to pasc data format).
        """
        num = list(byte)[0]
        # pad = num & 7
        # padded = pad != 0
        npad = num & 7
        lpad = num & (7 << 5)

        return PADFLAG(lzcpad=lpad, noisepad=npad)

    def generate_stream(coded):
        """
        Encode information saved in a coded object (according to pasc data format).

        Arguments
        =========
        coded : Coded
            Data to be encoded.

        Returns
        =======
        result : bytes
            Encoded information about coded object.
        """

        iflag = Format.generate_infoflag(coded)
        pflag = Format.generate_padflag(coded)
        if coded.start != 0:
            result = np.array([coded.start, len(coded.blzc), len(
                coded.bnoise)]).astype(np.uint32).tobytes()
        else:
            result = np.array([len(coded.blzc), len(coded.bnoise)]).astype(
                np.uint32).tobytes()
        return iflag + pflag + result + coded.blzc + coded.bnoise

    def read_stream(byte):
        """
        Decode stream of information encoded in bytes.

        Arguments
        =========
        byte : bytes
            Information to be encoded.

        Returns
        =======
        result : STREAM
            Information about the data and encoding.
        """

        iflag = Format.read_infoflag(byte[0:1])
        pflag = Format.read_padflag(byte[1:2])

        if not iflag.startvalue:
            vstart = np.frombuffer(byte[2:6], np.uint32, 1)[0]
            lzcstart = 6
        else:
            vstart = 0
            lzcstart = 2
        lzclen = np.frombuffer(byte[lzcstart:], np.uint32, 1)[0]
        noiselen = np.frombuffer(byte[lzcstart + 4:], np.uint32, 1)[0]
        lzcstart += 8

        noisestart = lzcstart + lzclen

        blzc = byte[lzcstart:noisestart]
        bnoise = byte[noisestart:noiselen + noisestart]
        next_stream = noiselen + noisestart

        result = STREAM(is_32=iflag.is_32, startvalue=vstart, npad=pflag.noisepad,
                        lpad=pflag.lzcpad, blzc=blzc, bnoise=bnoise, next_stream=next_stream)
        return result


if __name__ == '__main__':
    pass
