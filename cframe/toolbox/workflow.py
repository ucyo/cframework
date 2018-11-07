#!/usr/bin/env python
# coding: utf-8
"""
An envelope class for different modifiers.
"""
import os
from time import time
# from cframe.toolbox.qualityassessment import QA, xz_compression
from cframe.objects.arrays.predictionarray import PredictionArray
from cframe.objects.arrays.integerarray import IntegerArray
from cframe.objects.arrays import floatarray as fa
import numpy as np

from functools import namedtuple as nt


class Workflow(object):
    """An envelope object for compression frameworks"""

    def __init__(self, mapper, sequencer, predictor, subtractor, encoder):
        self.mapper = mapper
        self.sequencer = sequencer
        self.predictor = predictor
        self.subtractor = subtractor
        self.encoder = encoder

    def __repr__(self):
        res = [x.name for x in [self.mapper, self.sequencer,
                                self.predictor, self.subtractor, self.encoder]]
        return ",".join(res)

    def compress(self, floatarray, seqstart, feeder=None, *args, **kwargs):
        start = time()
        if isinstance(floatarray, np.ndarray):
            # necessary for parallel execution
            floatarray = fa.FloatArray(floatarray)
        iarr = self.mapper.map(floatarray)
        seq = self.sequencer.flatten(seqstart, iarr)

        # The feeder improves runtime speed via pre-allocation of memory
        if feeder is not None:
            feed = feeder(self.predictor, *args, **kwargs)
            _, parr = feed.feed(seq)
        else:
            predictions = []
            predictor = self.predictor(*args, **kwargs)
            for value in seq.data:
                prediction = predictor.predict()
                predictions.append(prediction)
                predictor.update(value)
            prediction_ndarray = np.array(predictions).reshape(seq.shape)
            parr = PredictionArray(prediction_ndarray)
        rarr = self.subtractor.subtract(parr, iarr)
        coded = self.encoder.encode(rarr, seqstart, floatarray.shape)
        return coded

        # R = nt('Compression', 'farr, iarr, seq, parr, rarr, coded')
        # result = R(floatarray, iarr, seq, parr, rarr, coded)
        # return result


    def decompress(self, coded):
        residuals = self.encoder.decode(coded)
        rarr = linear_sequencer_rev(residuals, coded.start)
        tmp = recon_iarr(rarr, self.predictor, coded.start, self.subtractor)
        iarr = IntegerArray(linear_iarr_rev(tmp.reshape(coded.shape), coded.start))
        farr = self.mapper.revmap(iarr)
        return farr

        # R = nt('Compression', 'farr, iarr, seq, parr, rarr, coded')
        # result = R(farr, iarr, None, None, rarr, coded)
        # return result


def linear_sequencer_rev(rarr, startnode):
    return np.roll(rarr, -startnode)


def linear_iarr_rev(iarr, startnode):
    return np.roll(iarr, startnode)


def reverse(residuals, predictor, subtractor, *args, **kwargs):
    # TODO Optimize using np.array and intervene with Feeder
    p = predictor(*args, **kwargs)
    for k in residuals.ravel():
        val = p.predict()
        truth = subtractor._single(val, k)
        p.update(truth)
        yield truth


def recon_iarr(residuals, predictor, startnode, subtractor, *args, **kwargs):
    reconstructed = reverse(residuals, predictor, subtractor)
    result = np.array([x for x in reconstructed])
    return result


if __name__ == '__main__':
    from cframe.toolbox.feeder import SeqFeeder
    from cframe.objects.arrays import floatarray as fl
    from cframe.modifier.mapper.lindstrom import Lindstrom
    from cframe.modifier.mapper.rawbinary import RawBinary
    from cframe.modifier.mapper.ordered import Ordered
    from cframe.modifier.mapper.raw import Raw
    from cframe.modifier.sequencer.linear import Linear
    from cframe.modifier.predictor.lastvalue import LastValue
    from cframe.modifier.subtractor.xor import XOR
    from cframe.modifier.encoder.f1 import F1

    data = fl.FloatArray.from_data('pre', 'tas', decode_times=False)
    data = fl.FloatArray.from_data('pre', 'ua', decode_times=False)
    data = fl.FloatArray.from_numpy(data.array[0,5,:,:])
    wf = Workflow(mapper=Lindstrom, sequencer=Linear, predictor=LastValue, subtractor=XOR, encoder=F1)

    coded = wf.compress(data, 0, SeqFeeder)
    result = wf.decompress(coded.coded)
    equal = ((data == result) | (np.isnan(data) & np.isnan(result))).all()
    print(equal)
