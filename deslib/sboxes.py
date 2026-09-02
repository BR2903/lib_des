"""S-boxes de DES: el unico componente no lineal del cifrado."""

from .tables import SBOXES


def sbox_lookup(box: int, six_bits: int) -> int:
    """6 bits -> 4 bits a traves de la S-box indicada (box de 0 a 7).

    El bit mas significativo y el menos significativo forman el numero de
    fila (0-3); los cuatro del medio, la columna (0-15).
    """
    row = ((six_bits >> 5) & 1) * 2 + (six_bits & 1)
    col = (six_bits >> 1) & 0xF
    return SBOXES[box][row][col]


def substitute(value48: int) -> int:
    """48 bits -> 32 bits pasando ocho grupos de 6 por sus S-boxes."""
    out = 0
    for i in range(8):
        six = (value48 >> (42 - 6 * i)) & 0x3F
        out = (out << 4) | sbox_lookup(i, six)
    return out
