"""Permutacion generica y rotacion circular sobre enteros."""


def permute(value: int, table: tuple, input_width: int) -> int:
    """Reordena los bits de value segun table.

    value se interpreta con el bit 1 del estandar en la posicion mas
    significativa (MSB first). El bit numerado p ocupa el desplazamiento
    input_width - p, de ahi la resta.

    La salida mide len(table) bits, no input_width: por eso esta misma
    funcion sirve para permutar (IP, P), reducir (PC-1, PC-2) y expandir
    (E, cuya tabla repite posiciones).
    """
    out = 0
    for pos in table:
        bit = (value >> (input_width - pos)) & 1
        out = (out << 1) | bit
    return out


def rotate_left28(value: int, n: int) -> int:
    """Rotacion circular a la izquierda dentro de 28 bits."""
    return ((value << n) | (value >> (28 - n))) & 0x0FFFFFFF
