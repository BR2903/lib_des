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
