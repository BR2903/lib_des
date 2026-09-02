"""Operacion completa sobre un bloque de 64 bits."""

from .feistel import des_round
from .permutation import permute
from .tables import IP, IP_INV


def des_block(block: int, subkeys: list) -> int:
    """Bloque de 64 bits -> 64 bits.

    Cifra o descifra segun el orden de las subkeys: la estructura Feistel es
    identica en ambos sentidos, no hace falta invertir f.

    Orden: IP -> 16 rondas -> R16||L16 -> IP^-1. El intercambio final (R
    antes que L al concatenar) es imprescindible; sin el, el descifrado no
    recupera el plaintext.
    """
    if len(subkeys) != 16:
        raise ValueError(f"hacen falta 16 subkeys, llegaron {len(subkeys)}")

    bits = permute(block, IP, 64)
    L = (bits >> 32) & 0xFFFFFFFF
    R = bits & 0xFFFFFFFF

    for subkey in subkeys:
        L, R = des_round(L, R, subkey)

    return permute((R << 32) | L, IP_INV, 64)
