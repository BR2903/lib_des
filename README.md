# deslib

Implementación de **DES (Data Encryption Standard)** en Python puro, escrita
desde la especificación FIPS PUB 46-3.

Lab 1 de Cryptography (ECMC) — Yachay Tech University.

No se usa ninguna librería criptográfica. Las permutaciones, las S-boxes, el
key schedule, la función de Feistel y las 16 rondas están implementados desde
la especificación.

## Requisitos

- Python 3.11+
- `pytest` solo para los tests

La librería no tiene dependencias externas.

## Instalación

```bash
git clone <URL-DEL-REPO>
cd <carpeta>
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install pytest
```

## Uso

```python
from deslib import des_encrypt_block, des_decrypt_block

key = bytes.fromhex("133457799BBCDFF1")
pt  = bytes.fromhex("0123456789ABCDEF")

ct = des_encrypt_block(key, pt)
print(ct.hex().upper())                    # 85E813540F0AB405
print(des_decrypt_block(key, ct) == pt)    # True
```

La key y el bloque deben medir **exactamente 8 bytes**. Cualquier otra longitud
lanza `ValueError`.

### API pública

| Función | Descripción |
|---|---|
| `des_encrypt_block(key, plaintext)` | Cifra un bloque de 8 bytes |
| `des_decrypt_block(key, ciphertext)` | Descifra un bloque de 8 bytes |
| `des_key_schedule(key)` | Devuelve las 16 subkeys de 48 bits |
| `des_check_parity(key)` | `True` si cada byte tiene paridad impar |

También se exponen los componentes internos para inspección y pruebas:
`permute`, `rotate_left28`, `sbox_lookup`, `substitute`, `feistel_f`,
`des_round` y `des_block`.

```python
from deslib import des_key_schedule, sbox_lookup

subkeys = des_key_schedule(key)
print(f"{subkeys[0]:012X}")        # 1B02EFFC7072
print(sbox_lookup(0, 0b100101))    # 8
```

## Tests

```bash
pytest
```

La suite cubre lo que exige el laboratorio:

- Vector conocido en ambas direcciones
- Round keys k1 y k16
- Round trip con 20 bloques aleatorios más casos límite
- Efecto avalancha al cambiar un bit del plaintext y un bit efectivo de la key
- Rechazo de keys y bloques de 7 y 9 bytes
- Convención de bits: varios tests fallan si el bit 1 se interpreta como LSB

## Convención de bits

**El bit 1 del estándar es el más significativo.** Un bloque de 8 bytes se
convierte a entero con `int.from_bytes(datos, "big")`, y el bit numerado `p` en
las tablas ocupa el desplazamiento `input_width - p`:

```python
bit = (value >> (input_width - pos)) & 1
```

Interpretar el bit 1 como LSB produciría un cifrado internamente consistente
—cifra y descifra sin error— pero incompatible con el estándar y con cualquier
otra implementación de DES. El vector conocido no coincidiría. La suite incluye
tests específicos para esta convención.

El estado interno son enteros de Python; las cadenas de `'0'` y `'1'` solo
aparecen en los tests, para hacer legibles algunos casos.

## Estructura

```
deslib/
  __init__.py         reexporta la API pública
  tables.py           tablas del estándar (IP, IP⁻¹, E, P, PC-1, PC-2, S-boxes)
  permutation.py      permute genérica y rotación circular de 28 bits
  sboxes.py           sbox_lookup y substitute
  key_schedule.py     des_key_schedule y des_check_parity
  feistel.py          feistel_f y des_round
  des_core.py         des_block: IP → 16 rondas → intercambio → IP⁻¹
  api.py              des_encrypt_block y des_decrypt_block
tests/
  test_des.py
```

El núcleo contiene únicamente operaciones criptográficas: no imprime, no lee
archivos y no pide entrada por teclado.

## Notas de implementación

**Una sola rutina de permutación.** `permute` sirve para IP, IP⁻¹, E, P, PC-1 y
PC-2. La salida mide lo mismo que la tabla, no lo mismo que la entrada, así que
la misma función permuta (IP, P), reduce (PC-1, PC-2) y expande (E, cuya tabla
repite 16 posiciones).

**Cifrar y descifrar comparten el núcleo.** La estructura Feistel es idéntica en
ambos sentidos; solo cambia el orden de las subkeys (`subkeys[::-1]`). No hace
falta invertir `f`, que además no es invertible: las S-boxes van de 6 bits a 4 y
pierden información.

**El intercambio final no se omite.** Tras la ronda 16 se concatena `R` antes
que `L`. Sin ese paso el cifrado parece funcionar pero el descifrado no recupera
el plaintext.

**Los bits de paridad no afectan al cifrado.** PC-1 descarta las posiciones 8,
16, … 64. Dos keys que solo difieran en esos bits producen el mismo ciphertext,
y hay un test que lo comprueba. `des_check_parity` informa sobre la paridad pero
no rechaza ninguna key: el estándar no lo exige.

## Limitaciones

**DES no es seguro hoy.** La key efectiva es de 56 bits, lo que da un espacio de
2⁵⁶ ≈ 7,2 × 10¹⁶ claves. En 1998 la EFF recuperó una key por fuerza bruta en 56
horas con una máquina de US$250.000; en 2006 COPACOBANA lo hizo en unos 6,4 días
con hardware de US$10.000. La debilidad no está en la estructura Feistel ni en
las S-boxes, sino en la longitud de la key. Esta implementación es un ejercicio
didáctico y no debe usarse para proteger información real.

**Solo opera sobre un bloque.** La librería implementa DES tal como lo define el
estándar: una función de 64 bits a 64 bits. Cifrar mensajes de longitud
arbitraria requiere además un padding y un modo de operación (CBC, CTR), que
quedan fuera del alcance de este laboratorio.

**No se detectan claves débiles.** Existen cuatro keys para las que las 16
subkeys resultan idénticas, y seis pares semi-débiles. La librería no las
rechaza.

## Referencia

FIPS PUB 46-3, *Data Encryption Standard (DES)*, NIST, 1999.
