"""DES desde cero — VERSION DE UN SOLO ARCHIVO PARA COLAB.

Misma implementacion que el paquete des/, pegada en un solo archivo para
poder correrla en un notebook sin instalar nada.

Representacion interna: cadenas de caracteres '0' y '1'.
"""

# ===== tables.py =====
IP = [
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17, 9, 1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7,
]
IP_INV = [
    40, 8, 48, 16, 56, 24, 64, 32,
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9, 49, 17, 57, 25,
]
E = [
    32, 1, 2, 3, 4, 5,
    4, 5, 6, 7, 8, 9,
    8, 9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32, 1,
]
P = [
    16, 7, 20, 21,
    29, 12, 28, 17,
    1, 15, 23, 26,
    5, 18, 31, 10,
    2, 8, 24, 14,
    32, 27, 3, 9,
    19, 13, 30, 6,
    22, 11, 4, 25,
]
PC1 = [
    57, 49, 41, 33, 25, 17, 9,
    1, 58, 50, 42, 34, 26, 18,
    10, 2, 59, 51, 43, 35, 27,
    19, 11, 3, 60, 52, 44, 36,
    63, 55, 47, 39, 31, 23, 15,
    7, 62, 54, 46, 38, 30, 22,
    14, 6, 61, 53, 45, 37, 29,
    21, 13, 5, 28, 20, 12, 4,
]
PC2 = [
    14, 17, 11, 24, 1, 5,
    3, 28, 15, 6, 21, 10,
    23, 19, 12, 4, 26, 8,
    16, 7, 27, 20, 13, 2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32,
]
SHIFTS = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
SBOXES = [
    [[14,4,13,1,2,15,11,8,3,10,6,12,5,9,0,7],
     [0,15,7,4,14,2,13,1,10,6,12,11,9,5,3,8],
     [4,1,14,8,13,6,2,11,15,12,9,7,3,10,5,0],
     [15,12,8,2,4,9,1,7,5,11,3,14,10,0,6,13]],
    [[15,1,8,14,6,11,3,4,9,7,2,13,12,0,5,10],
     [3,13,4,7,15,2,8,14,12,0,1,10,6,9,11,5],
     [0,14,7,11,10,4,13,1,5,8,12,6,9,3,2,15],
     [13,8,10,1,3,15,4,2,11,6,7,12,0,5,14,9]],
    [[10,0,9,14,6,3,15,5,1,13,12,7,11,4,2,8],
     [13,7,0,9,3,4,6,10,2,8,5,14,12,11,15,1],
     [13,6,4,9,8,15,3,0,11,1,2,12,5,10,14,7],
     [1,10,13,0,6,9,8,7,4,15,14,3,11,5,2,12]],
    [[7,13,14,3,0,6,9,10,1,2,8,5,11,12,4,15],
     [13,8,11,5,6,15,0,3,4,7,2,12,1,10,14,9],
     [10,6,9,0,12,11,7,13,15,1,3,14,5,2,8,4],
     [3,15,0,6,10,1,13,8,9,4,5,11,12,7,2,14]],
    [[2,12,4,1,7,10,11,6,8,5,3,15,13,0,14,9],
     [14,11,2,12,4,7,13,1,5,0,15,10,3,9,8,6],
     [4,2,1,11,10,13,7,8,15,9,12,5,6,3,0,14],
     [11,8,12,7,1,14,2,13,6,15,0,9,10,4,5,3]],
    [[12,1,10,15,9,2,6,8,0,13,3,4,14,7,5,11],
     [10,15,4,2,7,12,9,5,6,1,13,14,0,11,3,8],
     [9,14,15,5,2,8,12,3,7,0,4,10,1,13,11,6],
     [4,3,2,12,9,5,15,10,11,14,1,7,6,0,8,13]],
    [[4,11,2,14,15,0,8,13,3,12,9,7,5,10,6,1],
     [13,0,11,7,4,9,1,10,14,3,5,12,2,15,8,6],
     [1,4,11,13,12,3,7,14,10,15,6,8,0,5,9,2],
     [6,11,13,8,1,4,10,7,9,5,0,15,14,2,3,12]],
    [[13,2,8,4,6,15,11,1,10,9,3,14,5,0,12,7],
     [1,15,13,8,10,3,7,4,12,5,6,11,0,14,9,2],
     [7,11,4,1,9,12,14,2,0,6,10,13,15,3,5,8],
     [2,1,14,7,4,10,8,13,15,12,9,0,3,5,6,11]],
]


# ===== padding.py =====
BLOQUE_BYTES = 8
BLOQUE_BITS = 64


def aplicar_padding(datos):
    faltantes = BLOQUE_BYTES - (len(datos) % BLOQUE_BYTES)
    relleno = bytes([faltantes] * faltantes)
    return datos + relleno


def quitar_padding(datos):
    if len(datos) == 0:
        raise ValueError("no hay datos que despadear")
    if len(datos) % BLOQUE_BYTES != 0:
        raise ValueError(f"la longitud debe ser multiplo de {BLOQUE_BYTES}, llegaron {len(datos)}")
    n = datos[-1]
    if n < 1 or n > BLOQUE_BYTES:
        raise ValueError(f"padding invalido: el ultimo byte vale {n}")
    if datos[-n:] != bytes([n] * n):
        raise ValueError("padding invalido: los ultimos bytes no son todos iguales")
    return datos[:-n]


def a_binario(datos):
    bina = []
    for i in datos:
        parte = f"{i:08b}"
        bina.append(parte)
    return "".join(bina)


def de_binario(cadena):
    if len(cadena) % 8 != 0:
        raise ValueError(f"la cadena debe tener un multiplo de 8 bits, llegaron {len(cadena)}")
    numeros = []
    for inicio in range(0, len(cadena), 8):
        parte = cadena[inicio:inicio + 8]
        numeros.append(int(parte, 2))
    return bytes(numeros)


def a_bloques(cadena):
    bloques = []
    for inicio in range(0, len(cadena), BLOQUE_BITS):
        bloque = cadena[inicio:inicio + BLOQUE_BITS]
        bloques.append(bloque)
    return bloques


def de_bloques(bloques):
    return "".join(bloques)


# ===== core.py =====
# ---------------------------------------------------------------------------
# Operaciones basicas sobre bits
# ---------------------------------------------------------------------------

def permutar(bits, tabla):
    """Reordena bits segun una tabla de posiciones.

    La salida mide lo mismo que la tabla, no lo mismo que la entrada: por eso
    esta misma funcion sirve para permutar (IP, P), reducir (PC-1, PC-2) y
    expandir (E, cuya tabla repite posiciones).

    Las tablas del estandar estan en base 1, de ahi el -1 al indexar.
    """
    resultado = []
    for posicion in tabla:
        resultado.append(bits[posicion - 1])
    return "".join(resultado)


def rotar(bits, n):
    """Rotacion circular a la izquierda de n posiciones."""
    return bits[n:] + bits[:n]


def xor(a, b):
    """XOR bit a bit entre dos cadenas de la misma longitud."""
    if len(a) != len(b):
        raise ValueError(
            f"a y b deben tener la misma longitud, llegaron {len(a)} y {len(b)}"
        )
    resultado = []
    for i in range(len(a)):
        resultado.append(str(int(a[i]) ^ int(b[i])))
    return "".join(resultado)


# ---------------------------------------------------------------------------
# Key schedule
# ---------------------------------------------------------------------------

def generar_subkeys(key_bytes):
    """Key de 8 bytes -> lista de 16 subkeys de 48 bits.

    PC-1 descarta los 8 bits de paridad (posiciones 8, 16, ... 64), dejando 56
    bits utiles que se parten en dos mitades de 28. En cada ronda ambas mitades
    rotan a la izquierda y PC-2 selecciona 48 de los 56 bits resultantes.
    """
    if len(key_bytes) != 8:
        raise ValueError(f"la clave debe ser de 8 bytes, llegaron {len(key_bytes)}")

    key56 = permutar(a_binario(key_bytes), PC1)
    C = key56[:28]
    D = key56[28:]

    subkeys = []
    for ronda in range(16):
        n = SHIFTS[ronda]
        C = rotar(C, n)
        D = rotar(D, n)
        subkeys.append(permutar(C + D, PC2))
    return subkeys


# ---------------------------------------------------------------------------
# Funcion f
# ---------------------------------------------------------------------------

def sustituir(bits48):
    """48 bits -> 32 bits a traves de las 8 S-boxes.

    Cada grupo de 6 bits entra a su propia caja. El primer y ultimo bit del
    grupo forman el numero de fila (0-3) y los cuatro del medio la columna
    (0-15). Las S-boxes son el unico elemento no lineal de DES.
    """
    if len(bits48) != 48:
        raise ValueError(f"se esperaban 48 bits, llegaron {len(bits48)}")

    salida = []
    for i in range(8):
        grupo = bits48[i * 6:(i + 1) * 6]
        fila = int(grupo[0] + grupo[5], 2)
        columna = int(grupo[1:5], 2)
        valor = SBOXES[i][fila][columna]
        salida.append(f"{valor:04b}")
    return "".join(salida)


def funcion_f(R, subkey):
    """R de 32 bits + subkey de 48 bits -> 32 bits."""
    expandido = permutar(R, E)
    mezclado = xor(expandido, subkey)
    sustituido = sustituir(mezclado)
    return permutar(sustituido, P)


# ---------------------------------------------------------------------------
# Rondas Feistel
# ---------------------------------------------------------------------------

def procesar_bloque(bloque, subkeys):
    """Un bloque de 64 bits -> 64 bits.

    Cifra o descifra segun el orden en que se le pasen las subkeys: la
    estructura Feistel es identica en ambos sentidos (FIPS 46-3, seccion de
    decryption).
    """
    if len(bloque) != 64:
        raise ValueError(f"el bloque debe ser de 64 bits, llegaron {len(bloque)}")
    if len(subkeys) != 16:
        raise ValueError(f"hacen falta 16 subkeys, llegaron {len(subkeys)}")

    bits = permutar(bloque, IP)
    L = bits[:32]
    R = bits[32:]

    for ronda in range(16):
        # La asignacion multiple evita pisar L antes de usarlo en el XOR.
        L, R = R, xor(L, funcion_f(R, subkeys[ronda]))

    # Intercambio final: se concatena R antes que L.
    return permutar(R + L, IP_INV)


def cifrar_bloque(bloque, subkeys):
    return procesar_bloque(bloque, subkeys)


def descifrar_bloque(bloque, subkeys):
    return procesar_bloque(bloque, subkeys[::-1])


# ===== API de alto nivel =====
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


# ===== verificacion =====

if __name__ == "__main__":

    def hex_a_bits(h):
        return "".join(f"{int(c, 16):04b}" for c in h)

    def bits_a_hex(b):
        return "".join(f"{int(b[i:i+4], 2):X}" for i in range(0, len(b), 4))

    key_bits = hex_a_bits("133457799BBCDFF1")
    key_bytes = bytes(int(key_bits[i:i + 8], 2) for i in range(0, 64, 8))
    plaintext = hex_a_bits("0123456789ABCDEF")

    subkeys = generar_subkeys(key_bytes)
    ciphertext = cifrar_bloque(plaintext, subkeys)

    print("=== test vector oficial ===")
    print("key        : 133457799BBCDFF1")
    print("plaintext  : 0123456789ABCDEF")
    print("ciphertext :", bits_a_hex(ciphertext))
    print("esperado   : 85E813540F0AB405")
    print("coincide   :", bits_a_hex(ciphertext) == "85E813540F0AB405")
    print("descifrado :", descifrar_bloque(ciphertext, subkeys) == plaintext)

    print()
    print("=== mensajes completos ===")
    for texto in ["Hola", "hola n 漢 🎉", "un mensaje mas largo que un solo bloque"]:
        c = cifrar_mensaje(texto, "holacomo")
        d = descifrar_mensaje(c, "holacomo")
        print(f"  {texto!r:45} -> {len(c)} bytes -> vuelta OK: {d == texto}")

    print()
    try:
        descifrar_mensaje(cifrar_mensaje("secreto", "holacomo"), "otrakey1")
    except ValueError as e:
        print("key equivocada detectada:", e)

    print()
    print("=== modo ECB: bloques repetidos ===")
    c = cifrar_mensaje("AAAAAAAA" * 3, "holacomo")
    for i in range(0, len(c), 8):
        print("  bloque", i // 8 + 1, ":", c[i:i + 8].hex().upper())
    print("  (los tres primeros son identicos: los patrones sobreviven)")
