"""Generacion de las 16 subkeys de 48 bits a partir de la key de 64."""

from .permutation import permute, rotate_left28
from .tables import PC1, PC2, SHIFTS


def des_key_schedule(key: bytes) -> list:
    """Key de 8 bytes -> lista de 16 subkeys de 48 bits (enteros).

    PC-1 descarta los 8 bits de paridad (posiciones 8, 16, ... 64) dejando 56
    bits utiles, partidos en dos mitades de 28. En cada ronda ambas mitades
    rotan a la izquierda segun SHIFTS y PC-2 selecciona 48 de los 56 bits.

    Las 16 rotaciones suman 28, asi que C16 == C0 y D16 == D0.
    """
    if len(key) != 8:
        raise ValueError(f"la key debe ser de 8 bytes, llegaron {len(key)}")

    k56 = permute(int.from_bytes(key, "big"), PC1, 64)
    C = (k56 >> 28) & 0x0FFFFFFF
    D = k56 & 0x0FFFFFFF

    subkeys = []
    for r in range(16):
        C = rotate_left28(C, SHIFTS[r])
        D = rotate_left28(D, SHIFTS[r])
        subkeys.append(permute((C << 28) | D, PC2, 56))
    return subkeys


def des_check_parity(key: bytes) -> bool:
    """True si cada byte de la key tiene paridad impar.

    El estandar define el ultimo bit de cada byte como bit de paridad. DES no
    lo usa criptograficamente (PC-1 lo descarta), asi que una key con paridad
    incorrecta cifra igual; esta funcion solo informa.
    """
    if len(key) != 8:
        raise ValueError(f"la key debe ser de 8 bytes, llegaron {len(key)}")
    return all(bin(b).count("1") % 2 == 1 for b in key)
