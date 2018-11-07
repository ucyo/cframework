#!/usr/bin/env python
# coding: utf-8
"""
Shuffle Compression Library.

Shuffling bits.

Usage:
  demo.py info FILE
  demo.py subsetting FILE N
  demo.py shannon FILE
  demo.py ensemble FILE
  demo.py parallel [FILE...] [--climate]
  demo.py compress WFNR FILE [--subset=<size>]
  demo.py -h | --help
  demo.py --version

Options:
  -h --help           Show this screen
  -v --version        Show version
  -s --subset=<size>  Size of subset [default: None]
  -c --climate        Run with climate models
"""
from docopt import docopt
import numpy as np

def read_inputfile(ifile):
    _, bits, shape, _ = ifile.rsplit('.', 3)
    bits = bits[1:]
    shape = tuple(list(int(x) for x in shape.split('x')))
    return np.fromfile(ifile, dtype='float{}'.format(bits)).reshape(shape)

def check_arrays(arr1, arr2):
    eq = ((arr1 == arr2) | (np.isnan(arr1) & np.isnan(arr2))).all()
    return eq

if __name__ == '__main__':
    from time import time

    # Mapper
    from cframe.modifier.mapper.lindstrom import Lindstrom
    from cframe.modifier.mapper.ordered import Ordered
    from cframe.modifier.mapper.rawbinary import RawBinary
    from cframe.modifier.mapper.raw import Raw

    # Sequencer
    from cframe.modifier.sequencer.linear import Linear

    # Predictor
    from cframe.modifier.predictor.lastvalue import LastValue
    from cframe.modifier.predictor.stride import Stride
    from cframe.modifier.predictor.akumuli import Akumuli
    from cframe.modifier.predictor.strideconfidence import StrideConfidence
    from cframe.modifier.predictor.twostride import TwoStride

    # Subtractor
    from cframe.modifier.subtractor.xor import XOR
    from cframe.modifier.subtractor.floatingpoint import FPD

    # Encoder
    from cframe.modifier.encoder.f1 import F1
    from cframe.modifier.encoder.raw import RawEncoder

    # Tools
    from cframe.toolbox.workflow import Workflow

    # Objects
    from cframe.objects.arrays.floatarray import FloatArray

    arguments = docopt(__doc__, version='0.10.1')
    if not arguments['--climate']:
        data = read_inputfile(arguments['FILE'][0])

    workflows = {
        1 : Workflow(Ordered, Linear, LastValue, XOR, F1),
        2 : Workflow(Ordered, Linear, TwoStride, XOR, F1),
        3 : Workflow(Ordered, Linear, Akumuli, XOR, F1),
    }

    if arguments['info']:
        print('Filename:', arguments['FILE'][0])
        print('shape:   ', data.shape)
    elif arguments['compress']:
        if arguments['--subset'] != 'None':
            value = int(arguments['--subset'])
            from cframe.toolbox.subsetting import Subset
            sub = Subset.subset(data, value)
            data = sub
        key = int(arguments['WFNR'])
        w = workflows[key]
        start = time()
        compressed = w.compress(data, 0)
        dtime = time()
        uncompressed = w.decompress(compressed)
        end = time()
        result_check = check_arrays(data, uncompressed)

        cbytes = len(compressed.blzc)+len(compressed.bnoise)
        print('successfull:  ', result_check)
        print('filename:     ', arguments['FILE'][0])
        print('nbytes:       ', data.nbytes)
        print('compressed:   ', cbytes)
        print('cr:           ', cbytes/data.nbytes)
        print('bfp:          ', (8*cbytes)/data.size, "[{}]".format(str(data.dtype)[-2:]))
        print('compr. [sec]: ', dtime - start)
        print('dcmpr. [sec]: ', end - dtime)
    elif arguments['subsetting']:
        from cframe.toolbox.subsetting import Subset
        value = int(arguments['N'])
        sub = Subset.subset(data, value)
        print(sub.shape)
    elif arguments['shannon']:
        from cframe.toolbox.shannon.entropy import shannon_binary
        entropy = shannon_binary(data.flatten(), 32)
        print(entropy)
    elif arguments['parallel']:
        from cframe.toolbox.parallel import ParallelProcessWorkflow
        from cframe.toolbox.feeder import SeqFeeder
        if arguments['--climate']:

            # climate compression
            for var in ['ua', 'tas']:
                print("Compression of {}".format(var))
                a = FloatArray.from_data('pre', var)
                if var=='ua':
                    a = FloatArray.from_numpy(a.array[0,12,:,:])
                workflows = [Workflow(m, Linear, p, sb, RawEncoder)
                             for m in [Ordered, Raw]
                             for p in [LastValue, Akumuli, TwoStride, StrideConfidence]
                             for sb in [XOR, FPD]
                            ]
                par = ParallelProcessWorkflow()
                compressions = par.compress(workflows, a, 0, SeqFeeder)
                import operator
                res = {x[0]:x[1].nbytes/a.nbytes for x in compressions if not isinstance(x[1], str)}
                sorted_x = sorted(res.items(), key=operator.itemgetter(1))
                print("#"*25)
                for i,v in sorted_x:
                    print('{:50s} \t {:.5f}'.format(i,v))
        else:
            from cframe.toolbox.parallel import ParallelProcessWorkflow
            from cframe.toolbox.feeder import SeqFeeder

            par = ParallelProcessWorkflow()
            compressions = par.compress(workflows.values(), data, 0, SeqFeeder)
            import operator
            res = {x[0]:x[1].nbytes/data.nbytes for x in compressions if not isinstance(x[1], str)}
            sorted_x = sorted(res.items(), key=operator.itemgetter(1))
            print("#"*25)
            for i,v in sorted_x:
                print('{:50s} \t {:.5f}'.format(i,v))
    elif arguments['ensemble']:
        from cframe.modifier.predictor.ensemble import LastBest, MostRight

        predictors = [LastValue, TwoStride, Akumuli]
        w = Workflow(Ordered, Linear, MostRight, XOR, F1)
        start = time()
        compressed = w.compress(data, 0, None, predictors)
        cbytes = len(compressed.blzc)+len(compressed.bnoise)
        print(cbytes/data.nbytes)

