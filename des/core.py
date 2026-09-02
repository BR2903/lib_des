"""Nucleo del algoritmo DES, implementado desde la especificacion FIPS PUB 46-3.

Todas las funciones de este modulo trabajan con cadenas de caracteres '0' y '1'.
La conversion desde y hacia bytes vive en padding.py.
"""

from .padding import a_binario
from .tables import IP, IP_INV, E, P, PC1, PC2, SHIFTS, SBOXES


# ---------------------------------------------------------------------------
# Operaciones basicas sobre bits
# ---------------------------------------------------------------------------

def permutar(bits, tabla):
    """Reordena bits segun una tabla de posiciones.

    La salida mide lo mismo que la tabla, no lo mismo que la entrada: por eso
    esta misma funcion sirve para permutar (IP, P), reducir (PC-1, PC-2) y
    expandir (E, cuya tabla repite posiciones).

    Las tablas del estandar estan en base 1, de ahi el -1 al indexar.
    """
    resultado = []
    for posicion in tabla:
        resultado.append(bits[posicion - 1])
    return "".join(resultado)


def rotar(bits, n):
    """Rotacion circular a la izquierda de n posiciones."""
    return bits[n:] + bits[:n]


def xor(a, b):
    """XOR bit a bit entre dos cadenas de la misma longitud."""
    if len(a) != len(b):
        raise ValueError(
            f"a y b deben tener la misma longitud, llegaron {len(a)} y {len(b)}"
        )
    resultado = []
    for i in range(len(a)):
        resultado.append(str(int(a[i]) ^ int(b[i])))
    return "".join(resultado)


# ---------------------------------------------------------------------------
# Key schedule
# ---------------------------------------------------------------------------

def generar_subkeys(key_bytes):
    """Key de 8 bytes -> lista de 16 subkeys de 48 bits.

    PC-1 descarta los 8 bits de paridad (posiciones 8, 16, ... 64), dejando 56
    bits utiles que se parten en dos mitades de 28. En cada ronda ambas mitades
    rotan a la izquierda y PC-2 selecciona 48 de los 56 bits resultantes.
    """
    if len(key_bytes) != 8:
        raise ValueError(f"la clave debe ser de 8 bytes, llegaron {len(key_bytes)}")

    key56 = permutar(a_binario(key_bytes), PC1)
    C = key56[:28]
    D = key56[28:]

    subkeys = []
    for ronda in range(16):
        n = SHIFTS[ronda]
        C = rotar(C, n)
        D = rotar(D, n)
        subkeys.append(permutar(C + D, PC2))
    return subkeys


# ---------------------------------------------------------------------------
# Funcion f
# ---------------------------------------------------------------------------

def sustituir(bits48):
    """48 bits -> 32 bits a traves de las 8 S-boxes.

    Cada grupo de 6 bits entra a su propia caja. El primer y ultimo bit del
    grupo forman el numero de fila (0-3) y los cuatro del medio la columna
    (0-15). Las S-boxes son el unico elemento no lineal de DES.
    """
    if len(bits48) != 48:
        raise ValueError(f"se esperaban 48 bits, llegaron {len(bits48)}")

    salida = []
    for i in range(8):
        grupo = bits48[i * 6:(i + 1) * 6]
        fila = int(grupo[0] + grupo[5], 2)
        columna = int(grupo[1:5], 2)
        valor = SBOXES[i][fila][columna]
        salida.append(f"{valor:04b}")
    return "".join(salida)


def funcion_f(R, subkey):
    """R de 32 bits + subkey de 48 bits -> 32 bits."""
    expandido = permutar(R, E)
    mezclado = xor(expandido, subkey)
    sustituido = sustituir(mezclado)
    return permutar(sustituido, P)


# ---------------------------------------------------------------------------
# Rondas Feistel
# ---------------------------------------------------------------------------

def procesar_bloque(bloque, subkeys):
    """Un bloque de 64 bits -> 64 bits.

    Cifra o descifra segun el orden en que se le pasen las subkeys: la
    estructura Feistel es identica en ambos sentidos (FIPS 46-3, seccion de
    decryption).
    """
    if len(bloque) != 64:
        raise ValueError(f"el bloque debe ser de 64 bits, llegaron {len(bloque)}")
    if len(subkeys) != 16:
        raise ValueError(f"hacen falta 16 subkeys, llegaron {len(subkeys)}")

    bits = permutar(bloque, IP)
    L = bits[:32]
    R = bits[32:]

    for ronda in range(16):
        # La asignacion multiple evita pisar L antes de usarlo en el XOR.
        L, R = R, xor(L, funcion_f(R, subkeys[ronda]))

    # Intercambio final: se concatena R antes que L.
    return permutar(R + L, IP_INV)


def cifrar_bloque(bloque, subkeys):
    return procesar_bloque(bloque, subkeys)


def descifrar_bloque(bloque, subkeys):
    return procesar_bloque(bloque, subkeys[::-1])
