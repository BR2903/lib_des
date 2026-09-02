"""Suite de tests de deslib.

Cubre los tests exigidos por el laboratorio: vector conocido, round keys,
round trip, efecto avalancha, entradas invalidas y convencion de bits.

    pytest

Los tests que necesitan datos aleatorios usan una semilla fija. La distancia
de Hamming del efecto avalancha sigue una binomial(64, 0.5), asi que un
ensayo cae fuera del rango [20, 44] aproximadamente una vez de cada 640; con
datos aleatorios sin semilla la suite fallaria de vez en cuando sin que nada
este mal en la implementacion.
"""

import random

import pytest

from deslib import (
    des_block,
    des_check_parity,
    des_decrypt_block,
    des_encrypt_block,
    des_key_schedule,
    des_round,
    feistel_f,
    permute,
    rotate_left28,
    sbox_lookup,
    substitute,
)
from deslib.tables import IP, IP_INV, PC1, SBOXES

KEY = bytes.fromhex("133457799BBCDFF1")
PLAINTEXT = bytes.fromhex("0123456789ABCDEF")
CIPHERTEXT = bytes.fromhex("85E813540F0AB405")

SEMILLA = 20260902


def peso_hamming(a: bytes, b: bytes) -> int:
    """Numero de bits en que difieren dos bloques."""
    return bin(int.from_bytes(a, "big") ^ int.from_bytes(b, "big")).count("1")


# ---------------------------------------------------------------------------
# Vector conocido
# ---------------------------------------------------------------------------

def test_vector_conocido_cifrado():
    assert des_encrypt_block(KEY, PLAINTEXT) == CIPHERTEXT


def test_vector_conocido_descifrado():
    assert des_decrypt_block(KEY, CIPHERTEXT) == PLAINTEXT


# ---------------------------------------------------------------------------
# Round keys
# ---------------------------------------------------------------------------

def test_round_keys_k1_y_k16():
    subkeys = des_key_schedule(KEY)
    assert f"{subkeys[0]:012X}" == "1B02EFFC7072"
    assert f"{subkeys[15]:012X}" == "CB3D8B0E17F5"


def test_key_schedule_produce_16_subkeys_de_48_bits():
    subkeys = des_key_schedule(KEY)
    assert len(subkeys) == 16
    assert all(0 <= s < (1 << 48) for s in subkeys)


def test_key_schedule_subkeys_distintas():
    assert len(set(des_key_schedule(KEY))) == 16


def test_key_schedule_ignora_bits_de_paridad():
    """PC-1 descarta el ultimo bit de cada byte: no afecta al cifrado."""
    otra = bytes(b ^ 0x01 for b in KEY)
    assert des_key_schedule(otra) == des_key_schedule(KEY)
    assert des_encrypt_block(otra, PLAINTEXT) == CIPHERTEXT


# ---------------------------------------------------------------------------
# Round trip
# ---------------------------------------------------------------------------

def test_round_trip_20_bloques():
    rng = random.Random(SEMILLA)
    key = rng.randbytes(8)
    for _ in range(20):
        bloque = rng.randbytes(8)
        assert des_decrypt_block(key, des_encrypt_block(key, bloque)) == bloque


def test_round_trip_varias_keys():
    rng = random.Random(SEMILLA + 1)
    for _ in range(20):
        key = rng.randbytes(8)
        bloque = rng.randbytes(8)
        assert des_decrypt_block(key, des_encrypt_block(key, bloque)) == bloque


def test_round_trip_casos_limite():
    casos = [b"\x00" * 8, b"\xff" * 8, b"\x80" + b"\x00" * 7, b"\x00" * 7 + b"\x01"]
    for bloque in casos:
        assert des_decrypt_block(KEY, des_encrypt_block(KEY, bloque)) == bloque


# ---------------------------------------------------------------------------
# Efecto avalancha
#
# Cambiar un bit de la entrada debe alterar cerca de la mitad de los bits del
# ciphertext. El criterio principal es el promedio, que es lo que mide el
# efecto; el rango individual [20, 44] que pide el laboratorio se comprueba
# despues, con la semilla fija que garantiza reproducibilidad.
# ---------------------------------------------------------------------------

def test_avalancha_al_cambiar_un_bit_del_plaintext():
    rng = random.Random(SEMILLA)
    distancias = []
    for _ in range(20):
        key = rng.randbytes(8)
        p1 = rng.randbytes(8)
        posicion = rng.randrange(64)
        p2 = (int.from_bytes(p1, "big") ^ (1 << posicion)).to_bytes(8, "big")
        distancias.append(
            peso_hamming(des_encrypt_block(key, p1), des_encrypt_block(key, p2))
        )

    promedio = sum(distancias) / len(distancias)
    assert 28 <= promedio <= 36, f"promedio {promedio}, se esperaba cerca de 32"
    assert all(20 <= d <= 44 for d in distancias), f"distancias: {distancias}"


def test_avalancha_al_cambiar_un_bit_efectivo_de_la_key():
    """Se cambia un bit que PC-1 conserva, nunca uno de paridad.

    Los bits de paridad son las posiciones 8, 16, ... 64 del estandar, que en
    el entero (MSB first) corresponden a los desplazamientos 0, 8, ... 56.
    """
    efectivos = [b for b in range(64) if b % 8 != 0]
    rng = random.Random(SEMILLA + 2)
    distancias = []
    for _ in range(20):
        k1 = rng.randbytes(8)
        bloque = rng.randbytes(8)
        posicion = rng.choice(efectivos)
        k2 = (int.from_bytes(k1, "big") ^ (1 << posicion)).to_bytes(8, "big")
        distancias.append(
            peso_hamming(des_encrypt_block(k1, bloque), des_encrypt_block(k2, bloque))
        )

    promedio = sum(distancias) / len(distancias)
    assert 28 <= promedio <= 36, f"promedio {promedio}, se esperaba cerca de 32"
    assert all(20 <= d <= 44 for d in distancias), f"distancias: {distancias}"


def test_bit_de_paridad_no_produce_avalancha():
    """Cambiar un bit de paridad no cambia nada: dH = 0.

    El contraste con los dos tests anteriores (dH cerca de 32) es la
    demostracion empirica de por que la key efectiva es de 56 bits y no 64.
    """
    otra = bytes(b ^ 0x01 for b in KEY)
    assert peso_hamming(
        des_encrypt_block(KEY, PLAINTEXT), des_encrypt_block(otra, PLAINTEXT)
    ) == 0


# ---------------------------------------------------------------------------
# Entradas invalidas
# ---------------------------------------------------------------------------

def test_rechaza_keys_de_7_y_9_bytes():
    for key in [b"\x00" * 7, b"\x00" * 9]:
        with pytest.raises(ValueError):
            des_encrypt_block(key, PLAINTEXT)
        with pytest.raises(ValueError):
            des_decrypt_block(key, CIPHERTEXT)
        with pytest.raises(ValueError):
            des_key_schedule(key)


def test_rechaza_bloques_de_7_y_9_bytes():
    for bloque in [b"\x00" * 7, b"\x00" * 9]:
        with pytest.raises(ValueError):
            des_encrypt_block(KEY, bloque)
        with pytest.raises(ValueError):
            des_decrypt_block(KEY, bloque)


def test_des_block_rechaza_numero_de_subkeys_incorrecto():
    subkeys = des_key_schedule(KEY)
    with pytest.raises(ValueError):
        des_block(0, subkeys[:15])


# ---------------------------------------------------------------------------
# Convencion de bits: el bit 1 del estandar es el MSB
# ---------------------------------------------------------------------------

def test_permute_extrae_el_bit_1_como_msb():
    """La tabla (1,) debe devolver el bit mas significativo de la entrada.

    Con la convencion invertida (bit 1 = LSB) estos asserts se intercambian.
    """
    assert permute(0b10000000, (1,), 8) == 1
    assert permute(0b01111111, (1,), 8) == 0


def test_permute_extrae_el_ultimo_bit_como_lsb():
    assert permute(0b00000001, (8,), 8) == 1
    assert permute(0b11111110, (8,), 8) == 0


def test_tabla_identidad_devuelve_el_valor_intacto():
    identidad = tuple(range(1, 9))
    for valor in [0b10000000, 0b00000001, 0b10110010]:
        assert permute(valor, identidad, 8) == valor


def test_tabla_invertida_da_el_espejo():
    """Comprobacion explicita de la orientacion de los bits."""
    invertida = tuple(range(8, 0, -1))
    assert permute(0b10000000, invertida, 8) == 0b00000001


def test_ip_primera_posicion_toma_el_bit_58():
    """IP empieza con 58: el primer bit de la salida es el bit 58 de la entrada.

    Con numeracion MSB first, el bit 58 de un valor de 64 bits esta en el
    desplazamiento 64 - 58 = 6.
    """
    valor = 1 << 6
    assert (permute(valor, IP, 64) >> 63) & 1 == 1


def test_ip_inv_deshace_ip():
    rng = random.Random(SEMILLA)
    for _ in range(10):
        valor = int.from_bytes(rng.randbytes(8), "big")
        assert permute(permute(valor, IP, 64), IP_INV, 64) == valor


def test_permute_conserva_el_numero_de_unos():
    valor = int.from_bytes(PLAINTEXT, "big")
    assert bin(permute(valor, IP, 64)).count("1") == bin(valor).count("1")


def test_pc1_descarta_los_bits_de_paridad():
    """Los bits en posiciones multiplo de 8 no aparecen en la salida."""
    for paridad in range(8, 65, 8):
        valor = 1 << (64 - paridad)
        assert permute(valor, PC1, 64) == 0


# ---------------------------------------------------------------------------
# Componentes individuales
# ---------------------------------------------------------------------------

def test_sbox_ejemplo_de_la_especificacion():
    """S1(100101) = 1000, con fila 11 = 3 y columna 0010 = 2."""
    assert sbox_lookup(0, 0b100101) == 0b1000


def test_sbox_esquinas_de_s1():
    assert sbox_lookup(0, 0b000000) == 14
    assert sbox_lookup(0, 0b111111) == 13


def test_sbox_todas_las_salidas_caben_en_4_bits():
    for box in range(8):
        for entrada in range(64):
            assert 0 <= sbox_lookup(box, entrada) <= 15


def test_sbox_cada_fila_es_permutacion_de_0_a_15():
    """Propiedad estructural del estandar: detecta errores de transcripcion."""
    for caja in SBOXES:
        for fila in caja:
            assert sorted(fila) == list(range(16))


def test_substitute_reduce_48_a_32_bits():
    assert substitute((1 << 48) - 1) < (1 << 32)


def test_rotate_left28():
    assert rotate_left28(0b1101, 1) == 0b11010
    assert rotate_left28(1 << 27, 1) == 1              # el MSB da la vuelta
    assert rotate_left28(0x0ABCDEF, 28) == 0x0ABCDEF   # vuelta completa


def test_feistel_f_devuelve_32_bits():
    subkeys = des_key_schedule(KEY)
    assert feistel_f(0x12345678, subkeys[0]) < (1 << 32)


def test_des_round_intercambia_las_mitades():
    """El L nuevo es exactamente el R anterior."""
    subkeys = des_key_schedule(KEY)
    L, R = 0xAAAAAAAA, 0x55555555
    nuevo_L, _ = des_round(L, R, subkeys[0])
    assert nuevo_L == R


# ---------------------------------------------------------------------------
# Paridad
# ---------------------------------------------------------------------------

def test_check_parity_key_valida():
    assert des_check_parity(KEY) is True


def test_check_parity_key_invalida():
    assert des_check_parity(bytes(b ^ 0x01 for b in KEY)) is False


def test_check_parity_rechaza_longitud_invalida():
    with pytest.raises(ValueError):
        des_check_parity(b"\x00" * 7)
