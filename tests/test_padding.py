"""Tests de la capa de preparacion (padding, conversion a bits, bloques).

Correr desde la raiz del proyecto:
    pytest
"""

import pytest

from des.padding import (
    aplicar_padding,
    quitar_padding,
    a_binario,
    de_binario,
    a_bloques,
    de_bloques,
)


# ---------------------------------------------------------------------------
# aplicar_padding
# ---------------------------------------------------------------------------

def test_padding_mensaje_corto():
    """4 bytes -> faltan 4 -> se agregan cuatro bytes con valor 4."""
    assert aplicar_padding(b"hola") == b"hola\x04\x04\x04\x04"


def test_padding_falta_uno():
    """7 bytes -> falta 1 -> se agrega un byte con valor 1."""
    assert aplicar_padding(b"Cifrado") == b"Cifrado\x01"


def test_padding_bloque_completo():
    """8 bytes exactos -> se agrega un bloque ENTERO de relleno.

    Este es el caso que parece innecesario pero es obligatorio: sin el,
    quien descifra no podria distinguir relleno de mensaje real.
    """
    assert aplicar_padding(b"Mensajes") == b"Mensajes" + b"\x08" * 8


def test_padding_vacio():
    """Mensaje vacio -> un bloque completo de relleno."""
    assert aplicar_padding(b"") == b"\x08" * 8


def test_padding_siempre_multiplo_de_8():
    for n in range(0, 40):
        datos = b"a" * n
        assert len(aplicar_padding(datos)) % 8 == 0


def test_padding_valor_entre_1_y_8():
    for n in range(0, 40):
        resultado = aplicar_padding(b"a" * n)
        assert 1 <= resultado[-1] <= 8


# ---------------------------------------------------------------------------
# quitar_padding
# ---------------------------------------------------------------------------

def test_quitar_padding_recupera_original():
    for n in range(0, 40):
        original = b"a" * n
        assert quitar_padding(aplicar_padding(original)) == original


def test_quitar_padding_rechaza_vacio():
    with pytest.raises(ValueError):
        quitar_padding(b"")


def test_quitar_padding_rechaza_longitud_no_multiplo():
    with pytest.raises(ValueError):
        quitar_padding(b"hola")


def test_quitar_padding_rechaza_valor_fuera_de_rango():
    """Ultimo byte = 200: imposible que lo haya producido aplicar_padding."""
    basura = b"\x00" * 7 + b"\xc8"
    with pytest.raises(ValueError):
        quitar_padding(basura)


def test_quitar_padding_rechaza_valor_cero():
    with pytest.raises(ValueError):
        quitar_padding(b"\x00" * 8)


def test_quitar_padding_rechaza_relleno_inconsistente():
    """El ultimo byte dice 4 pero los otros tres no son 4.

    Este es el caso tipico de descifrar con la key equivocada: el ultimo
    byte cae en rango valido por casualidad, pero el resto es basura.
    """
    falso = b"hola" + b"\x91\x2f\xa8\x04"
    with pytest.raises(ValueError):
        quitar_padding(falso)


# ---------------------------------------------------------------------------
# a_binario / de_binario
# ---------------------------------------------------------------------------

def test_a_binario_valores_conocidos():
    assert a_binario(b"H") == "01001000"
    assert a_binario(b"Ho") == "0100100001101111"


def test_a_binario_ocho_bits_por_byte():
    for n in range(0, 20):
        assert len(a_binario(b"a" * n)) == n * 8


def test_a_binario_rellena_con_ceros():
    """El byte 1 debe salir como 00000001, no como '1'."""
    assert a_binario(b"\x01") == "00000001"


def test_de_binario_es_inverso():
    original = "hola ñ 漢 🎉".encode("utf-8")
    assert de_binario(a_binario(original)) == original


def test_de_binario_rechaza_longitud_invalida():
    with pytest.raises(ValueError):
        de_binario("0100100")  # 7 bits


# ---------------------------------------------------------------------------
# a_bloques / de_bloques
# ---------------------------------------------------------------------------

def test_bloques_de_64_bits():
    cadena = a_binario(aplicar_padding(b"hola"))
    bloques = a_bloques(cadena)
    assert len(bloques) == 1
    assert len(bloques[0]) == 64


def test_bloques_mensaje_de_8_bytes_da_dos_bloques():
    """8 bytes exactos + bloque de padding = 16 bytes = 2 bloques."""
    cadena = a_binario(aplicar_padding(b"Mensajes"))
    assert len(a_bloques(cadena)) == 2


def test_todos_los_bloques_miden_64():
    for n in range(0, 40):
        cadena = a_binario(aplicar_padding(b"a" * n))
        for bloque in a_bloques(cadena):
            assert len(bloque) == 64


def test_de_bloques_es_inverso():
    cadena = a_binario(aplicar_padding(b"un mensaje bastante mas largo"))
    assert de_bloques(a_bloques(cadena)) == cadena


# ---------------------------------------------------------------------------
# Ida y vuelta completa
# ---------------------------------------------------------------------------

def test_ida_y_vuelta_ascii():
    original = "hola mundo".encode("utf-8")
    datos = aplicar_padding(original)
    bloques = a_bloques(a_binario(datos))
    recuperado = quitar_padding(de_binario(de_bloques(bloques)))
    assert recuperado == original


def test_ida_y_vuelta_caracteres_multibyte():
    """La n y los kanji ocupan varios bytes: deben sobrevivir enteros."""
    original = "hola ñ 漢 🎉".encode("utf-8")
    datos = aplicar_padding(original)
    bloques = a_bloques(a_binario(datos))
    recuperado = quitar_padding(de_binario(de_bloques(bloques)))
    assert recuperado == original
    assert recuperado.decode("utf-8") == "hola ñ 漢 🎉"


def test_ida_y_vuelta_muchas_longitudes():
    for n in range(0, 50):
        original = ("á" * n).encode("utf-8")
        datos = aplicar_padding(original)
        bloques = a_bloques(a_binario(datos))
        recuperado = quitar_padding(de_binario(de_bloques(bloques)))
        assert recuperado == original