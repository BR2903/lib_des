from .tables import SBOXES


def sbox_lookup(box: int, six_bits: int) -> int:
    row = ((six_bits >> 5) & 1) * 2 + (six_bits & 1)
    col = (six_bits >> 1) & 0xF
    return SBOXES[box][row][col]


def substitute(value48: int) -> int:
    out = 0
    for i in range(8):
        six = (value48 >> (42 - 6 * i)) & 0x3F
        out = (out << 4) | sbox_lookup(i, six)
    return out
