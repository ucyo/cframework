#!/usr/bin/env python
"""
Subsetting FloatArray's for faster comparison.
"""

from itertools import combinations, product
import numpy as np
import xarray as xr
from cframe.objects.arrays.floatarray import FloatArray

class Subset:

    name = "Subset"

    @staticmethod
    def subset(obj, size):
        if isinstance(obj, np.ndarray):
            result,_ = randomsubset(obj, size)
        elif isinstance(obj, xr.DataArray):
            _, slices = randomsubset(obj.values, size)
            slices = {x: y for x, y in zip(obj.dims, slices)}
            result = obj.isel(**slices)
        elif isinstance(obj, FloatArray):
            array, _ = randomsubset(obj.array, size)
            result = FloatArray(array)
        else:
            raise TypeError("Can't understand type.")
        return result


def randomsubset(arr, N):
    assert ispossible(arr, N)

    sub = [0] * arr.ndim

    while arr[tuple([slice(None,x,None) for x in sub])].size < N:
        axis = np.random.choice([x for x in range(arr.ndim)], p=np.array(arr.shape)/np.sum(arr.shape))
        sub[axis] += 1 if arr.shape[axis] > sub[axis] else 0
    startix = tuple(np.random.randint(0, x - y + 1) for x, y in zip(arr.shape, sub))
    sli = [slice(x, x + y, None) for x, y in zip(startix, sub)]

    result = arr[sli].copy()
    return result, sli


def ispossible(arr, N):
    if arr.size < N:
        msg = "Array size too small for subsetting."
        raise Exception(msg)
    if arr.ndim <= 1:
        msg = "Dimensions size too small for subsetting."
        raise Exception(msg)
    return True


if __name__ == '__main__':
    shape = (128,64,47)
    arr = np.arange(np.prod(shape)).reshape(shape)

    for value in [10000, 100000, 1000, 100]:
        Subset.subset(arr, value)
