from .permutation import permute
from .sboxes import substitute
from .tables import E, P


def feistel_f(right: int, subkey: int) -> int:
    return permute(substitute(permute(right, E, 32) ^ subkey), P, 32)


def des_round(left: int, right: int, subkey: int) -> tuple:
    """Una ronda Feistel: (L, R) -> (R, L XOR f(R, k))."""
    return right, left ^ feistel_f(right, subkey)
