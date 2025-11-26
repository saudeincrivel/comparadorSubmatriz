import ctypes
from ctypes import CDLL, POINTER, c_int32
from ctypes import c_size_t, c_double
import numpy as np
import os


class MatchPos(ctypes.Structure):
    _fields_ = [("row", ctypes.c_size_t), ("col", ctypes.c_size_t)]


ND_POINTER_2 = np.ctypeslib.ndpointer(dtype=np.uint8, ndim=2, flags="C")

DLLPATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "lib",
    "projetocdll.so"
)
DLLPATH = os.path.normpath(DLLPATH)

mylib = ctypes.CDLL(DLLPATH)

mylib.match_positions.argtypes = [
    ND_POINTER_2,
    ctypes.c_size_t,
    ctypes.c_size_t,
    ND_POINTER_2,
    ctypes.c_size_t,
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.POINTER(MatchPos)),
]
mylib.match_positions.restype = ctypes.c_size_t

mylib.free_results.argtypes = [ctypes.POINTER(MatchPos)]
mylib.free_results.restype = None


def comparator(a, b):
    n, m = a.shape
    rows_b, cols_b = b.shape

    if rows_b > n or cols_b > m:
        return np.zeros((0, 2), dtype=np.uint32)

    results_ptr = ctypes.POINTER(MatchPos)()
    count = mylib.match_positions(a, n, m, b, rows_b, cols_b, ctypes.byref(results_ptr))

    arr = np.zeros((count, 2), dtype=np.uint32)

    for i in range(count):
        arr[i, 0] = results_ptr[i].row
        arr[i, 1] = results_ptr[i].col

    mylib.free_results(results_ptr)
    return arr


def teste():
    # resposta = [[4,8], [9,16]]
    x = np.array(
        [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 3, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 3, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 3, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 2, 2, 2, 2],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 2, 2, 2, 2],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 2, 2, 2, 2],
        ],
        np.uint8,
    )

    y = np.array([[3, 2, 2, 2, 2], [3, 2, 2, 2, 2], [3, 2, 2, 2, 2]], np.uint8)

    ocurrencias = comparator(x, y)
    print("Pares ocurrencias :")
    print(ocurrencias)
    return None


# teste();
