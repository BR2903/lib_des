"""Funcion f de DES y una ronda Feistel."""

from .permutation import permute
from .sboxes import substitute
from .tables import E, P


def feistel_f(right: int, subkey: int) -> int:
    """f(R, k) = P(S(E(R) XOR k)). 32 bits + 48 bits -> 32 bits.

    E expande R de 32 a 48 bits para que quepa el XOR con la subkey; las
    S-boxes devuelven el resultado a 32.
    """
    return permute(substitute(permute(right, E, 32) ^ subkey), P, 32)


def des_round(left: int, right: int, subkey: int) -> tuple:
    """Una ronda Feistel: (L, R) -> (R, L XOR f(R, k))."""
    return right, left ^ feistel_f(right, subkey)
