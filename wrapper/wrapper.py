
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
    ND_POINTER_2 = np.ctypeslib.ndpointer(dtype=np.uint8, 
                                      ndim=2,
                                      flags="C");

    mylib = ctypes.cdll.LoadLibrary(DLLPATH);

    mylib.mostra.argtypes = [ND_POINTER_2, ND_POINTER_2 , c_size_t, c_size_t, c_size_t, c_size_t];
    mylib.mostra.restype = ctypes.c_char_p;

    mylib.match.argtypes = [ND_POINTER_2, ND_POINTER_2 , c_size_t, c_size_t, c_size_t, c_size_t];
    mylib.match.restype = ctypes.c_char_p;
    
    [n,m] = a.shape;
    [rows_b, cols_b] = b.shape;

    if (rows_b > n or cols_b > m) :
        return buildArray("0 0");
    
    resposta = mylib.match(a, b,  n, m , rows_b, cols_b);
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
 

