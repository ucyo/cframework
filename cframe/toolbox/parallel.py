#!/usr/bin/env python
# coding: utf-8
"""
Parallel execution of benchmarks.
"""

import numpy as np
from multiprocessing import cpu_count, Array
from concurrent import futures
import ctypes

class ParallelProcessWorkflow:
    """
    Parallel execution of Benchmarks using Threads.
    
    Arguments
    =========
    floatarray : Floatarray
        Array to be compressed in parallel.
    start : int
        Start value for the compression process.
    feeder : Feeder
        Using a Feeder object for speed up.
    cpus : int
        Number of cores to be used.
    
    Returns
    =======
    result : None
        None
    """

    def compress(self, workflows, floatarray, start, feeder, cpus=None):
        if cpus is None:
            cpus = cpu_count()
        # Generate shared memory object
        mapping = {'float32':ctypes.c_float, 'float64':ctypes.c_double}
        shared_array_base = Array(mapping.get(str(floatarray.dtype)), floatarray.size)
        shared_array = np.ctypeslib.as_array(shared_array_base.get_obj())
        shared_array[:] = floatarray.flat[:]
        shared_array = shared_array.reshape(floatarray.shape)

        with futures.ProcessPoolExecutor(max_workers=cpus) as executor:
            jobs = {executor.submit(x.compress, shared_array, start, feeder): str(x) for wfID,x in enumerate(workflows)}
            try:
                for done in futures.as_completed(jobs):
                    name = jobs[done]
                    print('Compression: WF id:{} DONE!'.format(name))
                    try:
                        result = done.result()
                        yield (name, result)
                    except:
                        yield (name, "Error")
            except KeyboardInterrupt:
                _ = [k.cancel() for k in jobs.keys()]


    def decompress(self, workflows, results, cpus=None):
        if cpus is None:
            cpus = cpu_count()
        with futures.ThreadPoolExecutor(max_workers=cpus) as executor:
            jobs = {executor.submit(workflows[res[0]].decompress, res[1]):res[0] for res in results}
            try:
                for done in futures.as_completed(jobs):
                    name = jobs[done]
                    print('Decompression: WF id:{} DONE!'.format(name))
                    try:
                        result = done.result()
                        yield result
                    except:
                        raise
            except KeyboardInterrupt:
                _ = [k.cancel() for k in jobs.keys()]


if __name__ == '__main__':
    # Mapper
    from cframe.modifier.mapper.ordered import Ordered
    from cframe.modifier.mapper.raw import Raw

    # Sequencer
    from cframe.modifier.sequencer.linear import Linear

    # Predictor
    from cframe.modifier.predictor.lastvalue import LastValue
    from cframe.modifier.predictor.stride import Stride
    from cframe.modifier.predictor.akumuli import Akumuli
    from cframe.modifier.predictor.twostride import TwoStride
    from cframe.modifier.predictor.strideconfidence import StrideConfidence

    # Subtractor
    from cframe.modifier.subtractor.xor import XOR
    from cframe.modifier.subtractor.floatingpoint import FPD

    # Encoder
    from cframe.modifier.encoder.raw import RawEncoder

    # Feeder
    from cframe.toolbox.feeder import SeqFeeder

    from cframe.toolbox.workflow import Workflow
    from cframe.objects.arrays.floatarray import FloatArray

    import sys
    from cframe.toolbox.subsetting import Subset

    if len(sys.argv) < 2:
        raise Exception('Forgot the variable?')
    val = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    if sys.argv[1] == 'ua': 
        a = FloatArray.from_data('pre', 'ua')
        a = FloatArray.from_numpy(a.array[0,12,:,:])
        if val != 0:
            a = FloatArray.from_numpy(Subset.subset(a.array, val))
    elif sys.argv[1] in ('tas', 'pr'):
        a = FloatArray.from_data('pre', sys.argv[1])
        if val != 0:
            a = FloatArray.from_numpy(Subset.subset(a.array, val))
    else:
        raise Exception('Can not understand variable')
    original = a.array.nbytes
    print(a.array.shape)




    workflows = [Workflow(m, Linear, p, sb, RawEncoder)
                 for m in [Ordered, Raw]
                 for p in [LastValue, Akumuli, TwoStride, StrideConfidence]
                 for sb in [XOR, FPD]
                ]




    par = ParallelProcessWorkflow()
    compressions = par.compress(workflows, a, 0, SeqFeeder)
    import operator
    res = {x[0]:x[1].nbytes/original for x in compressions if not isinstance(x[1], str)}
    sorted_x = sorted(res.items(), key=operator.itemgetter(1))
    print("#"*25)
    for i,v in sorted_x:
        print('{:50s} \t {:.5f}'.format(i,v))
    # decompressions = par.decompress(workflows, compressions)
    # print([a==x for x in decompressions])