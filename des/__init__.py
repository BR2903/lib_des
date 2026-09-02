"""Implementacion de DES desde la especificacion (FIPS PUB 46-3).

Uso basico:

    from des import cifrar_mensaje, descifrar_mensaje

    c = cifrar_mensaje("hola mundo", "holacomo")
    print(descifrar_mensaje(c, "holacomo"))

MODO DE OPERACION: los bloques se cifran de forma independiente, es decir en
modo ECB. Bloques de plaintext identicos producen ciphertext identico, asi que
los patrones del mensaje sobreviven al cifrado. Es una limitacion conocida y
asumida: los modos de operacion (CBC, CTR) quedan fuera del alcance de este
laboratorio.
"""

from .core import (
    permutar,
    rotar,
    xor,
    generar_subkeys,
    sustituir,
    funcion_f,
    procesar_bloque,
    cifrar_bloque,
    descifrar_bloque,
)
from .padding import (
    aplicar_padding,
    quitar_padding,
    a_binario,
    de_binario,
    a_bloques,
    de_bloques,
)


def cifrar_mensaje(texto, key):
    """texto (str) + key (str de 8 bytes) -> ciphertext (bytes).

    El resultado son bytes arbitrarios: no es texto y no debe decodificarse.
    Para mostrarlo o guardarlo, usar .hex() o base64.
    """
    subkeys = generar_subkeys(key.encode("utf-8"))

    datos = aplicar_padding(texto.encode("utf-8"))
    bits = a_binario(datos)

    salida = []
    for bloque in a_bloques(bits):
        salida.append(cifrar_bloque(bloque, subkeys))

    return de_binario(de_bloques(salida))


def descifrar_mensaje(cifrado, key):
    """ciphertext (bytes) + key (str de 8 bytes) -> texto (str).

    Lanza ValueError si el padding resultante no es valido, lo que en la
    practica significa que la clave es incorrecta o los datos estan corruptos.
    """
    subkeys = generar_subkeys(key.encode("utf-8"))

    bits = a_binario(cifrado)

    salida = []
    for bloque in a_bloques(bits):
        salida.append(descifrar_bloque(bloque, subkeys))

    datos = de_binario(de_bloques(salida))
    return quitar_padding(datos).decode("utf-8")
