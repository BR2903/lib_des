# lib_des

Implementación de **DES (Data Encryption Standard)** en Python puro, escrita
desde la especificación **FIPS PUB 46-3**.

No se usa ninguna librería criptográfica. Las permutaciones, las S-boxes, el
key schedule, la función de Feistel y las 16 rondas están implementadas a mano.

Lab 1 de Cryptography — Yachay Tech University, ECMC.

> ⚠️ Proyecto didáctico. DES está obsoleto y no debe usarse para proteger
> información real. Ver [Limitaciones](#limitaciones).

## Requisitos

- Python 3.11 o superior
- Sin dependencias de ejecución
- `pytest` solo para correr los tests

## Instalación

El package aún no es instalable con `pip`. Hay que clonarlo y trabajar desde la
raíz del repositorio:

```bash
git clone https://github.com/BR2903/lib_des.git
cd lib_des
```

El `cd` es necesario: Python encuentra el package porque el directorio actual
está en `sys.path`. Desde cualquier otra carpeta, `import des` falla.

En Google Colab:

```python
!git clone https://github.com/BR2903/lib_des.git
%cd lib_des
```

## Uso

```python
from des import cifrar_mensaje, descifrar_mensaje

c = cifrar_mensaje("hola me llamo bryan", "holacomo")
print(c.hex().upper())
# 1BA668758DBE148D54F36B8D37E03AA9FE23947296533C82

print(descifrar_mensaje(c, "holacomo"))
# hola me llamo bryan
```

La key debe ocupar **exactamente 8 bytes**.

El resultado de `cifrar_mensaje` son bytes arbitrarios, no texto. No intentes
decodificarlo: para mostrarlo o guardarlo usa `.hex()` o base64.

### Cifrado de un solo bloque

Para operar directamente sobre un bloque de 64 bits, sin padding:

```python
from des import generar_subkeys, cifrar_bloque, a_binario, de_binario

subkeys = generar_subkeys(bytes.fromhex("133457799BBCDFF1"))
bloque = a_binario(bytes.fromhex("0123456789ABCDEF"))

cifrado = cifrar_bloque(bloque, subkeys)
print(de_binario(cifrado).hex().upper())
# 85E813540F0AB405
```

## API pública

### Capa de mensaje

| Función | Firma | Descripción |
|---|---|---|
| `cifrar_mensaje` | `(texto: str, key: str) -> bytes` | Aplica padding y cifra el mensaje completo en ECB. |
| `descifrar_mensaje` | `(cifrado: bytes, key: str) -> str` | Descifra, valida y quita el padding. |

### Capa de bloque

| Función | Firma | Descripción |
|---|---|---|
| `generar_subkeys` | `(key_bytes: bytes) -> list[str]` | Key de 8 bytes → 16 subkeys de 48 bits. |
| `cifrar_bloque` | `(bloque: str, subkeys: list[str]) -> str` | Cifra un bloque de 64 bits. |
| `descifrar_bloque` | `(bloque: str, subkeys: list[str]) -> str` | Descifra un bloque de 64 bits. |

### Padding y conversiones

| Función | Firma | Descripción |
|---|---|---|
| `aplicar_padding` | `(datos: bytes) -> bytes` | PKCS#5 hasta el siguiente múltiplo de 8 bytes. |
| `quitar_padding` | `(datos: bytes) -> bytes` | Quita y valida el padding. |
| `a_binario` | `(datos: bytes) -> str` | Bytes → cadena de `'0'` y `'1'`. |
| `de_binario` | `(cadena: str) -> bytes` | Cadena de bits → bytes. |
| `a_bloques` | `(cadena: str) -> list[str]` | Parte una cadena de bits en bloques de 64. |
| `de_bloques` | `(bloques: list[str]) -> str` | Une bloques en una sola cadena. |

## Estructura

```
lib_des/
├── des/
│   ├── __init__.py      capa de mensaje (padding + ECB)
│   ├── core.py          permutaciones, key schedule, función f, 16 rondas
│   ├── tables.py        IP, IP⁻¹, E, P, PC-1, PC-2, rotaciones, S-boxes
│   └── padding.py       PKCS#5 y conversiones bytes ↔ bits
├── tests/
│   ├── test_des.py      test vectors oficiales y propiedades del cifrado
│   └── test_padding.py  padding, conversiones y round trips
├── colab_des.ipynb      notebook generado (no editar a mano)
├── build_colab.py       genera colab_des.ipynb desde des/
└── reporte-lab1-des.md  reporte del laboratorio
```

## Representación interna

El estado interno son **cadenas de caracteres `'0'` y `'1'`**, no enteros. Las
conversiones desde y hacia `bytes` viven en `padding.py` (`a_binario`,
`de_binario`).

Es una decisión de legibilidad: las permutaciones y el key schedule se leen
directamente como reordenamientos de posiciones. El costo es rendimiento: cada
operación de bits recorre la cadena carácter por carácter.

## Convenciones

- **Tablas en base 1.** Todas las tablas de `tables.py` están transcritas tal
  como aparecen en FIPS PUB 46-3: la posición 1 es el bit más significativo.
  `permutar` resta 1 internamente para indexar.
- **`permutar` sirve para todo.** La salida mide lo mismo que la tabla, no lo
  mismo que la entrada. Por eso la misma función permuta (IP, P), reduce (PC-1,
  PC-2) y expande (E, cuya tabla repite posiciones).
- **Bits de paridad ignorados.** PC-1 descarta los bits 8, 16, …, 64 de la key.
  La librería no valida ni genera paridad.

## Tests

```bash
pip install pytest
python -m pytest -q
```

50 tests. Incluyen los test vectors oficiales de DES:

| Key | Plaintext | Ciphertext |
|---|---|---|
| `133457799BBCDFF1` | `0123456789ABCDEF` | `85E813540F0AB405` |
| `0000000000000000` | `0000000000000000` | `8CA64DE9C1B123A7` |
| `FFFFFFFFFFFFFFFF` | `FFFFFFFFFFFFFFFF` | `7359B2163E4EDC58` |
| `0101010101010101` | `95F8A5E5DD31D900` | `8000000000000000` |
| `7CA110454A1A6E57` | `01A1D6D039776742` | `690F5B0D9A26939B` |

Que estos pasen significa que la implementación es compatible con el estándar y
con cualquier otra implementación de DES.

## Notebook

`colab_des.ipynb` contiene toda la librería aplanada en un solo notebook, más
demostraciones de padding, ECB y comportamiento con key incorrecta.

**Se genera automáticamente.** No lo edites a mano: edita `des/` y regenera.

```bash
python build_colab.py
```

## Limitaciones

**DES no es seguro hoy.** La key efectiva es de 56 bits, lo que da un espacio de
2⁵⁶ ≈ 7,2 × 10¹⁶ claves. La debilidad no está en la estructura Feistel ni en las
S-boxes, sino en la longitud de la key.

**Modo ECB.** Los bloques se cifran de forma independiente, así que bloques de
plaintext idénticos producen ciphertext idéntico y los patrones del mensaje
sobreviven al cifrado. CBC y CTR quedan fuera del alcance de este laboratorio.

**No se detectan claves débiles.** Existen cuatro keys para las que las 16
subkeys resultan idénticas, y seis pares semi-débiles. La librería no las
rechaza.

**El unpadding no es autenticación.** Que el padding sea válido no garantiza que
la key sea correcta ni que los datos no hayan sido manipulados. Con una key
incorrecta, `descifrar_mensaje` lanza `ValueError` casi siempre, pero
aproximadamente 1 de cada 256 veces el padding resulta válido por azar y la
excepción que sale es `UnicodeDecodeError`.

**La key y el texto se codifican en UTF-8.** Un carácter fuera de ASCII ocupa
más de un byte, así que una key de 8 caracteres puede no ser una key de 8 bytes.
La librería no restringe la entrada a ASCII.

## Referencia

FIPS PUB 46-3, *Data Encryption Standard (DES)*, NIST, 1999.