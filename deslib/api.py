"""API publica de la libreria."""

from .des_core import des_block
from .key_schedule import des_check_parity, des_key_schedule


def _to_int(block: bytes, nombre: str) -> int:
    if len(block) != 8:
        raise ValueError(f"{nombre} debe ser de 8 bytes, llegaron {len(block)}")
    return int.from_bytes(block, "big")


def des_encrypt_block(key: bytes, plaintext: bytes) -> bytes:
    """Cifra un bloque de 8 bytes con una key de 8 bytes."""
    subkeys = des_key_schedule(key)
    return des_block(_to_int(plaintext, "el plaintext"), subkeys).to_bytes(8, "big")


def des_decrypt_block(key: bytes, ciphertext: bytes) -> bytes:
    """Descifra un bloque de 8 bytes con una key de 8 bytes."""
    subkeys = des_key_schedule(key)
    return des_block(_to_int(ciphertext, "el ciphertext"), subkeys[::-1]).to_bytes(8, "big")
