
import ctypes
from ctypes import CDLL, POINTER, c_int32
from ctypes import c_size_t, c_double
import numpy as np
import os 




DLLPATH =  os.getcwd() + "\dll\projetocdll.dll";

def buildArray(padrao ):
    splitado = padrao.split();
    array = [];
    i = 1;
    while ( i  < len ( splitado )):
        array.append ([ splitado[i-1], splitado[i] ]);
        i+=2;
    return np.array(array);


def comparator (a , b ):
    ND_POINTER_2 = np.ctypeslib.ndpointer(dtype=np.int32, 
                                      ndim=2,
                                      flags="C");

    mylib = ctypes.cdll.LoadLibrary(DLLPATH);

    mylib.mostra.argtypes = [ND_POINTER_2, ND_POINTER_2 , c_size_t, c_size_t, c_size_t, c_size_t];
    mylib.mostra.restype = ctypes.c_char_p;

    mylib.match.argtypes = [ND_POINTER_2, ND_POINTER_2 , c_size_t, c_size_t, c_size_t, c_size_t];
    mylib.match.restype = ctypes.c_char_p;
    # mylib.mostra.restype = None;

    [n,m] = a.shape;
    [rows_b, cols_b] = b.shape;

    if (rows_b > n or cols_b > m) :
        return buildArray("0 0");
    
    # print(f'dims ::: {n} {m}');
    
    A = np.arange(1, n*m+1, 1, dtype=np.int32).reshape(n, m, order="C");
    B = np.arange(1, rows_b*cols_b+1, 1, dtype=np.int32).reshape(rows_b,cols_b , order="C");

    for i in range (n):
        for j in range (m):
            A[i][j] = a[i][j];

    for i in range (rows_b):
        for j in range ( cols_b):
            B[i][j] = b[i][j];

    resposta = mylib.match(A, B,  n, m , rows_b, cols_b);
    return buildArray(resposta.decode("utf-8"));



def teste():
    # resposta = [[4,8], [9,16]]
    x = np.array([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
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
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 2, 2, 2, 2]], np.int32 );

    y = np.array([[3, 2, 2,2, 2],
    [3, 2, 2,2, 2],
    [3, 2, 2,2, 2]],np.int32 );

    ocurrencias = comparator(x,y);
    print("Pares ocurrencias :");
    print ( ocurrencias);
    return None;


# teste();
 

