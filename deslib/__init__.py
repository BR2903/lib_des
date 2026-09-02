"""DES implementado desde la especificacion FIPS PUB 46-3.

    from deslib import des_encrypt_block, des_decrypt_block

    K = bytes.fromhex("133457799BBCDFF1")
    C = des_encrypt_block(K, bytes.fromhex("0123456789ABCDEF"))

Convencion de bits: el bit 1 del estandar es el mas significativo (MSB first).
El estado interno son enteros de Python; las cadenas de '0' y '1' se usan solo
en los tests para hacer legibles algunos casos.
"""

from .api import des_decrypt_block, des_encrypt_block
from .des_core import des_block
from .feistel import des_round, feistel_f
from .key_schedule import des_check_parity, des_key_schedule
from .permutation import permute, rotate_left28
from .sboxes import sbox_lookup, substitute

__all__ = [
    "des_encrypt_block", "des_decrypt_block", "des_key_schedule",
    "des_check_parity", "des_block", "des_round", "feistel_f",
    "permute", "rotate_left28", "sbox_lookup", "substitute",
]
