def permute(value: int, table: tuple, input_width: int) -> int:
    out = 0
    for pos in table:
        bit = (value >> (input_width - pos)) & 1
        out = (out << 1) | bit
    return out


def rotate_left28(value: int, n: int) -> int:
    """Rotacion circular a la izquierda dentro de 28 bits."""
    return ((value << n) | (value >> (28 - n))) & 0x0FFFFFFF
