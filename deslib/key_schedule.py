from .permutation import permute, rotate_left28
from .tables import PC1, PC2, SHIFTS


def des_key_schedule(key: bytes) -> list:
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
    if len(key) != 8:
        raise ValueError(f"la key debe ser de 8 bytes, llegaron {len(key)}")
    return all(bin(b).count("1") % 2 == 1 for b in key)
