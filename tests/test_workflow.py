#!/usr/bin/env python
# coding: utf-8
"""
Tests for workflow process
"""

import pytest
import os
from cframe.toolbox.workflow import Workflow
from cframe.toolbox import get_bits
from cframe.objects.arrays.floatarray import FloatArray
from cframe.toolbox.feeder import SeqFeeder

# Mapper
from cframe.modifier.mapper.lindstrom import Lindstrom 
from cframe.modifier.mapper.rawbinary import RawBinary
from cframe.modifier.mapper.rawbinary import RawBinary
from cframe.modifier.mapper.raw import Raw
from cframe.modifier.mapper.ordered import Ordered

# Sequencer
from cframe.modifier.sequencer.linear import Linear

# Predictor
from cframe.modifier.predictor.lastvalue import LastValue
from cframe.modifier.predictor.stride import Stride

# Subtractor
from cframe.modifier.subtractor.xor import XOR
from cframe.modifier.subtractor.floatingpoint import FPD

# Encoder
from cframe.modifier.encoder.raw import RawEncoder

DATA = [
    FloatArray.from_data('pre', 'tas'),
    # FloatArray.from_data('pre', 'ua'),
]

MAP = [
    Lindstrom,
    RawBinary,
    Raw,
    Ordered,
]

SEQ = [
    Linear,
]

PRE = [
    LastValue,
    # Stride,
]

SUB = [
    XOR,
    FPD,
]

ENC = [
    RawEncoder,
]

START = [
    0,
    3,
]

@pytest.mark.parametrize('mapp', MAP)
@pytest.mark.parametrize('seq', SEQ)
@pytest.mark.parametrize('pre', PRE)
@pytest.mark.parametrize('sub', SUB)
@pytest.mark.parametrize('enc', ENC)
@pytest.mark.parametrize('data', DATA)
@pytest.mark.parametrize('start', START)
def test_full_workflow_chain(data, mapp, seq, pre, sub, enc, start):
    wf = Workflow(mapp, seq, pre, sub, enc)
    coded = wf.compress(data, start, SeqFeeder)
    result = wf.decompress(coded)
    assert result == data