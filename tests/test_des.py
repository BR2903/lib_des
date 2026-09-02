"""Tests del nucleo DES, validados contra test vectors conocidos.

Correr desde la raiz del proyecto:
    pytest
"""

import pytest

from des import (
    permutar,
    rotar,
    xor,
    generar_subkeys,
    sustituir,
    funcion_f,
    cifrar_bloque,
    descifrar_bloque,
    cifrar_mensaje,
    descifrar_mensaje,
)
from des.tables import IP, IP_INV, PC1


# ---------------------------------------------------------------------------
# Utilidades para los test vectors, que se publican en hexadecimal
# ---------------------------------------------------------------------------

def hex_a_bits(h):
    return "".join(f"{int(c, 16):04b}" for c in h)


def bits_a_hex(b):
    return "".join(f"{int(b[i:i+4], 2):X}" for i in range(0, len(b), 4))


# ---------------------------------------------------------------------------
# permutar
# ---------------------------------------------------------------------------

def test_permutar_ejemplo_manual():
    """Tabla [3, 1, 4, 2] sobre ABCD debe dar CADB."""
    assert permutar("ABCD", [3, 1, 4, 2]) == "CADB"


def test_permutar_salida_mide_lo_que_la_tabla():
    bits = "0" * 64
    assert len(permutar(bits, IP)) == 64
    assert len(permutar(bits, PC1)) == 56


def test_ip_inv_deshace_ip():
    bits = "0111001101100001011001110110110101101110011101100110011001100010"
    assert permutar(permutar(bits, IP), IP_INV) == bits


def test_permutar_no_crea_ni_destruye_unos():
    bits = "0111001101100001011001110110110101101110011101100110011001100010"
    assert permutar(bits, IP).count("1") == bits.count("1")


# ---------------------------------------------------------------------------
# rotar
# ---------------------------------------------------------------------------

def test_rotar_una_posicion():
    assert rotar("1101", 1) == "1011"


def test_rotar_dos_posiciones():
    assert rotar("1101", 2) == "0111"


def test_rotar_vuelta_completa():
    """Rotar tantas posiciones como bits deja la cadena igual."""
    assert rotar("1101", 4) == "1101"


# ---------------------------------------------------------------------------
# xor
# ---------------------------------------------------------------------------

def test_xor_basico():
    assert xor("1010", "0110") == "1100"
    assert xor("1111", "1111") == "0000"


def test_xor_es_su_propio_inverso():
    """La propiedad que hace posible el descifrado Feistel."""
    a, b = "10110010", "01101101"
    assert xor(xor(a, b), b) == a


def test_xor_rechaza_longitudes_distintas():
    with pytest.raises(ValueError):
        xor("101", "1010")


# ---------------------------------------------------------------------------
# S-boxes
# ---------------------------------------------------------------------------

def test_sbox_ejemplo_de_la_especificacion():
    """Entrada 100101 en S1: fila 11 = 3, columna 0010 = 2, salida 8."""
    assert sustituir("100101" + "0" * 42)[:4] == "1000"


def test_sbox_esquinas_de_s1():
    assert sustituir("0" * 48)[:4] == "1110"   # fila 0, col 0  -> 14
    assert sustituir("1" * 48)[:4] == "1101"   # fila 3, col 15 -> 13


def test_sbox_reduce_48_a_32():
    assert len(sustituir("0" * 48)) == 32


def test_sbox_rechaza_longitud_invalida():
    with pytest.raises(ValueError):
        sustituir("0" * 47)


# ---------------------------------------------------------------------------
# Key schedule
# ---------------------------------------------------------------------------

def test_key_schedule_produce_16_subkeys_de_48():
    subkeys = generar_subkeys(b"holacomo")
    assert len(subkeys) == 16
    assert all(len(s) == 48 for s in subkeys)


def test_key_schedule_subkeys_distintas():
    subkeys = generar_subkeys(b"holacomo")
    assert len(set(subkeys)) == 16


def test_key_schedule_rechaza_key_de_otro_tamano():
    for key in [b"", b"abc", b"nueve car"]:
        with pytest.raises(ValueError):
            generar_subkeys(key)


def test_key_schedule_ignora_bits_de_paridad():
    """Dos keys que solo difieran en los bits de paridad dan las mismas subkeys.

    PC-1 descarta las posiciones 8, 16, ... 64, asi que el ultimo bit de cada
    byte no interviene en el cifrado.
    """
    a = bytes([0x13, 0x34, 0x57, 0x79, 0x9B, 0xBC, 0xDF, 0xF1])
    b = bytes([x ^ 0x01 for x in a])   # cambia solo el ultimo bit de cada byte
    assert generar_subkeys(a) == generar_subkeys(b)


# ---------------------------------------------------------------------------
# funcion f
# ---------------------------------------------------------------------------

def test_funcion_f_devuelve_32_bits():
    subkeys = generar_subkeys(b"holacomo")
    R = "00000000000011100000011100000010"
    assert len(funcion_f(R, subkeys[0])) == 32


# ---------------------------------------------------------------------------
# TEST VECTOR OFICIAL
# ---------------------------------------------------------------------------

def test_vector_conocido_cifrado():
    """Test vector clasico de DES.

    key        133457799BBCDFF1
    plaintext  0123456789ABCDEF
    ciphertext 85E813540F0AB405
    """
    key_bits = hex_a_bits("133457799BBCDFF1")
    key_bytes = bytes(int(key_bits[i:i + 8], 2) for i in range(0, 64, 8))

    plaintext = hex_a_bits("0123456789ABCDEF")
    subkeys = generar_subkeys(key_bytes)

    ciphertext = cifrar_bloque(plaintext, subkeys)
    assert bits_a_hex(ciphertext) == "85E813540F0AB405"


def test_vector_conocido_descifrado():
    key_bits = hex_a_bits("133457799BBCDFF1")
    key_bytes = bytes(int(key_bits[i:i + 8], 2) for i in range(0, 64, 8))

    ciphertext = hex_a_bits("85E813540F0AB405")
    subkeys = generar_subkeys(key_bytes)

    plaintext = descifrar_bloque(ciphertext, subkeys)
    assert bits_a_hex(plaintext) == "0123456789ABCDEF"


def test_bloque_rechaza_tamano_invalido():
    subkeys = generar_subkeys(b"holacomo")
    with pytest.raises(ValueError):
        cifrar_bloque("0" * 63, subkeys)


# ---------------------------------------------------------------------------
# Capa de mensaje
# ---------------------------------------------------------------------------

def test_mensaje_ida_y_vuelta():
    for texto in ["", "Hola", "hola ñ 漢 🎉", "un mensaje mas largo que un bloque"]:
        cifrado = cifrar_mensaje(texto, "holacomo")
        assert descifrar_mensaje(cifrado, "holacomo") == texto


def test_mensaje_cifrado_es_multiplo_de_8_bytes():
    for n in range(0, 30):
        cifrado = cifrar_mensaje("a" * n, "holacomo")
        assert len(cifrado) % 8 == 0


def test_key_equivocada_es_detectada():
    """Con la clave incorrecta el padding resultante no valida."""
    cifrado = cifrar_mensaje("mensaje secreto", "holacomo")
    with pytest.raises(ValueError):
        descifrar_mensaje(cifrado, "otrakey1")


def test_ecb_bloques_repetidos_dan_ciphertext_repetido():
    """Limitacion conocida del modo ECB, documentada en el README.

    Este test no comprueba una virtud sino una debilidad: sirve para dejar
    constancia de que el comportamiento es el esperado y no un error.
    """
    cifrado = cifrar_mensaje("AAAAAAAA" * 3, "holacomo")
    bloques = [cifrado[i:i + 8] for i in range(0, len(cifrado), 8)]
    assert bloques[0] == bloques[1] == bloques[2]