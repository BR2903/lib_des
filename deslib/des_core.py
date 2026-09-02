"""Operacion completa sobre un bloque de 64 bits."""

from .feistel import des_round
from .permutation import permute
from .tables import IP, IP_INV


def des_block(block: int, subkeys: list) -> int:
    if len(subkeys) != 16:
        raise ValueError(f"hacen falta 16 subkeys, llegaron {len(subkeys)}")

    bits = permute(block, IP, 64)
    L = (bits >> 32) & 0xFFFFFFFF
    R = bits & 0xFFFFFFFF

    for subkey in subkeys:
        L, R = des_round(L, R, subkey)

    return permute((R << 32) | L, IP_INV, 64)
