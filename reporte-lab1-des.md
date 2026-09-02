# Laboratorio 1: Implementación de DES como librería de cifrado simétrico

**Curso:** Cryptography (ECMC)
**Escuela:** School of Mathematical and Computational Sciences — Yachay Tech University
**Profesor:** Cristhian Iza
**Estudiante:** Bryan
**Repositorio:** https://github.com/BR2903/lib_des

---

## 1. Objetivo

Implementar el Data Encryption Standard desde la especificación FIPS PUB 46-3,
sin usar librerías criptográficas, y empaquetarlo como una librería reutilizable
con API pública y suite de tests automáticos.

---

## 2. Pre-laboratorio

### 2.1 ¿Qué significa la primera entrada de la tabla IP?

La primera entrada de IP es **58**, y significa: *el primer bit de la salida es
el bit que ocupaba la posición 58 de la entrada*.

La dirección de lectura es la parte que se presta a confusión. La tabla no
indica a dónde va cada bit, sino de dónde viene: se recorren las posiciones del
resultado en orden (1, 2, 3, …) y en cada una se consulta la tabla para saber
qué bit traer.

Las primeras ocho entradas de IP son 58, 50, 42, 34, 26, 18, 10 y 2 — es decir,
el segundo bit de cada uno de los ocho bytes. IP reagrupa los bits por su
posición dentro del byte, una operación que era conveniente para el hardware de
los años setenta. No aporta seguridad criptográfica: la tabla es pública y
`IP⁻¹` la deshace exactamente.

### 2.2 ¿Por qué E expande de 32 a 48 bits?

Por dos razones, una operativa y otra criptográfica.

**Operativa:** la mitad derecha *R* tiene 32 bits y la subclave de ronda tiene
48. Sin igualar tamaños no se puede aplicar el XOR que introduce la clave en el
dato.

**Criptográfica:** E no rellena con ceros, sino que **repite 16 bits de la
entrada**. Los repetidos son exactamente el primero y el último de cada grupo de
cuatro: las posiciones 1, 4, 5, 8, 9, 12, …, 32. Al hacerlo, cada bit de
frontera entra a **dos S-boxes vecinas** en lugar de una.

La tabla se lee en filas de seis y cada fila alimenta una S-box:

```
32  1  2  3  4  5      ← el 32 y el 5 son prestados; 1-4 son propios
 4  5  6  7  8  9      ← el 4 y el 9 son prestados; 5-8 son propios
 8  9 10 11 12 13
```

Los grupos se solapan: el 5 cierra la primera fila y abre la segunda. Rellenar
con ceros habría igualado los tamaños igual, pero no habría aportado difusión.

### 2.3 Fila, columna y salida de S₁(100101₂)

Los seis bits se dividen de forma no contigua:

```
1 0 0 1 0 1
↑         ↑
└── fila ─┘     primer y último bit:  11₂ = 3
  └─────┘
   columna      los cuatro del medio: 0010₂ = 2
```

Consultando S₁ en la fila 3, columna 2, el valor es **8**, que en binario de
cuatro bits es **1000₂**.

Verificado en la implementación:

```python
>>> sbox_lookup(0, 0b100101)
8
```

### 2.4 ¿Qué posiciones elimina PC-1 y por qué DES tiene solo 56 bits efectivos?

PC-1 tiene 56 entradas, de modo que su salida mide 56 bits aunque la entrada
tenga 64. Las ocho posiciones que **no aparecen** en la tabla son los múltiplos
de 8: **8, 16, 24, 32, 40, 48, 56 y 64**, es decir el último bit de cada byte.

Esos son los **bits de paridad**. En el hardware de los años setenta servían para
detectar errores de transmisión: se elegían de forma que cada byte tuviera un
número impar de unos. No intervienen en el cifrado.

La consecuencia directa es que **dos claves que difieran únicamente en esos bits
producen exactamente el mismo texto cifrado**. La librería incluye un test que lo
comprueba, y el análisis de la sección 5.3 lo confirma empíricamente: cambiar un
bit de paridad produce una distancia de Hamming de 0 en el ciphertext, mientras
que cambiar un bit efectivo produce alrededor de 32.

Por eso el espacio de claves real es de 2⁵⁶ y no de 2⁶⁴.

---

## 3. Diseño de la librería

### 3.1 Estructura

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
  test_des.py         34 tests
```

El núcleo contiene únicamente operaciones criptográficas. No imprime, no lee
archivos y no solicita entrada por teclado, tal como exigen las reglas de
implementación.

### 3.2 API pública

| Función | Descripción |
|---|---|
| `des_encrypt_block(key, plaintext)` | Cifra un bloque de 8 bytes |
| `des_decrypt_block(key, ciphertext)` | Descifra un bloque de 8 bytes |
| `des_key_schedule(key)` | Devuelve las 16 subclaves de 48 bits |
| `des_check_parity(key)` | `True` si cada byte tiene paridad impar |

Tanto la clave como el bloque deben medir exactamente ocho bytes; cualquier otra
longitud lanza `ValueError`.

### 3.3 Representación interna

El estado de DES se maneja como **enteros de Python**, con operaciones bitwise.
Las cadenas de caracteres `'0'` y `'1'` aparecen solo en los tests, para hacer
legibles algunos casos concretos.

### 3.4 Convención de bits

**El bit 1 del estándar es el más significativo (MSB first).** Un bloque de ocho
bytes se convierte a entero con `int.from_bytes(datos, "big")`, y el bit numerado
*p* en las tablas ocupa el desplazamiento `input_width - p`:

```python
bit = (value >> (input_width - pos)) & 1
```

Interpretar el bit 1 como LSB produciría un cifrado **internamente consistente**
—cifraría y descifraría sin lanzar ningún error— pero incompatible con el
estándar y con cualquier otra implementación de DES. El vector conocido no
coincidiría, y el error sería difícil de localizar porque nada fallaría de forma
visible.

Por eso la suite incluye tests específicos para esta convención (sección 5.5).

### 3.5 Una sola rutina de permutación

`permute` implementa IP, IP⁻¹, E, P, PC-1 y PC-2. La clave está en que **la
salida mide lo mismo que la tabla, no lo mismo que la entrada**. Esto permite que
la misma función:

- **permute** cuando la tabla tiene tantas entradas como bits (IP: 64 → 64)
- **reduzca** cuando tiene menos (PC-1: 64 → 56; PC-2: 56 → 48)
- **expanda** cuando tiene más y repite posiciones (E: 32 → 48)

Seis de los componentes que exige el laboratorio salen de una función de cinco
líneas.

### 3.6 Cifrado y descifrado comparten el núcleo

`des_block` recibe la lista de subclaves y no sabe si está cifrando o
descifrando. La única diferencia es el orden:

```python
def des_decrypt_block(key, ciphertext):
    subkeys = des_key_schedule(key)
    return des_block(..., subkeys[::-1]).to_bytes(8, "big")
```

Esto es posible por la propiedad de las redes de Feistel. Dado que
`(a ⊕ b) ⊕ b = a`, aplicar las rondas con las subclaves invertidas deshace
exactamente lo que hicieron al cifrar.

No hace falta invertir la función *f* — y de hecho **no sería posible**: las
S-boxes van de 6 bits a 4, así que cuatro entradas distintas producen la misma
salida y la información se pierde. En el descifrado, *f* se ejecuta hacia
adelante igual que siempre; lo que se deshace es el XOR.

### 3.7 El intercambio final

Tras la ronda 16 se concatena **R antes que L**:

```python
return permute((R << 32) | L, IP_INV, 64)
```

Omitir este paso produce un cifrado que parece funcionar pero cuyo descifrado no
recupera el texto original.

---

## 4. Verificación contra vectores conocidos

### 4.1 Vector principal

| | |
|---|---|
| Clave | `133457799BBCDFF1` |
| Texto plano | `0123456789ABCDEF` |
| Texto cifrado obtenido | `85E813540F0AB405` |
| Texto cifrado esperado | `85E813540F0AB405` |

El descifrado de `85E813540F0AB405` con la misma clave devuelve
`0123456789ABCDEF`.

### 4.2 Subclaves de ronda

| Ronda | Subclave |
|---|---|
| k1 | `1B02EFFC7072` |
| k2 | `79AED9DBC9E5` |
| k3 | `55FC8A42CF99` |
| … | … |
| k15 | `BF918D3D3F0A` |
| k16 | `CB3D8B0E17F5` |

k1 y k16 coinciden con los valores especificados en el enunciado.

Una comprobación adicional propia: tras las 16 rotaciones se cumple que
**C₁₆ = C₀ y D₁₆ = D₀**. Los desplazamientos suman 4·1 + 12·2 = 28, que es
exactamente el tamaño de cada mitad, así que la clave da la vuelta completa. Este
invariante detecta los dos errores más frecuentes del key schedule: usar el
desplazamiento equivocado en alguna ronda, o rotar siempre desde C₀ en lugar de
acumular.

---

## 5. Suite de tests

34 tests, todos en verde:

```
$ pytest
================== test session starts ==================
collected 34 items
tests\test_des.py ..................................  [100%]
================== 34 passed in 0.25s ===================
```

### 5.1 Vector conocido

Cifrado y descifrado del par especificado en el enunciado.

### 5.2 Round trip

Cuarenta bloques en total: veinte con una clave fija y veinte con claves
distintas, más cuatro casos límite (todo ceros, todo unos, solo el bit más
significativo, solo el menos significativo). En todos se verifica
D_K(E_K(P)) = P.

### 5.3 Efecto avalancha

Se mide la distancia de Hamming entre dos textos cifrados cuyas entradas
difieren en un solo bit:

d_H(C, C′) = popcount(C ⊕ C′)

**Cambiando un bit del texto plano**, sobre 1000 ensayos:

| Métrica | Resultado | Referencia teórica |
|---|---|---|
| Promedio | 31,91 | 32,00 |
| Mínimo | 20 | — |
| Máximo | 42 | — |
| Fuera de [20, 44] | 0,00 % | 0,16 % |

**Cambiando un bit efectivo de la clave** (nunca uno de paridad), el
comportamiento es equivalente: promedio en torno a 32.

**Cambiando un bit de paridad de la clave**, la distancia es **exactamente 0**.

Ese contraste es la demostración empírica de la respuesta a la pregunta 2.4: los
bits de paridad no participan en el cifrado, y por eso la clave efectiva es de 56
bits y no de 64.

#### Propagación ronda a ronda

Midiendo la distancia después de cada ronda, con `0123456789ABCDEF` frente al
mismo bloque con un bit invertido:

| Ronda | Bits distintos |
|---|---|
| 1 | 1 |
| 2 | 6 |
| 3 | 22 |
| 4 | 32 |
| 5 | 30 |
| 8 | 29 |
| 12 | 36 |
| 16 | 37 |

La difusión completa se alcanza alrededor de la **cuarta ronda**: a partir de ahí
la diferencia oscila en torno a la mitad de los 64 bits. Las doce rondas
restantes no aumentan la difusión, sino que consolidan la resistencia frente al
criptoanálisis diferencial y lineal.

#### Nota metodológica sobre la aleatoriedad

Los tests con datos aleatorios usan **semilla fija**. La distancia de Hamming
sigue una distribución binomial(64; 0,5), de modo que un ensayo aislado cae fuera
del rango [20, 44] con probabilidad 0,156 %, aproximadamente **uno de cada 640**.

Con veinte ensayos por test y datos sin semilla, la probabilidad de que la suite
fallara en alguna ejecución era de alrededor del **3 %**, sin que nada estuviera
mal en la implementación. Durante el desarrollo se observó efectivamente un valor
de 17.

Una prueba de 20 000 ensayos confirmó que el comportamiento es el correcto:
promedio 32,00, con un 0,13 % de valores fuera del rango — coincidente con la
predicción teórica. La semilla fija hace la suite reproducible sin debilitar el
criterio: el test comprueba primero el **promedio** (28 ≤ media ≤ 36), que es lo
que realmente mide el efecto avalancha, y después el rango individual.

### 5.4 Entradas inválidas

Claves y bloques de 7 y 9 bytes son rechazados con `ValueError` explícito en
`des_encrypt_block`, `des_decrypt_block`, `des_key_schedule` y
`des_check_parity`. También se rechaza una lista de subclaves que no tenga
exactamente 16 elementos.

### 5.5 Convención de bits

Seis tests fallarían si el bit 1 se interpretara como LSB:

- `permute(0b10000000, (1,), 8) == 1` — la tabla `(1,)` extrae el MSB
- `permute(0b00000001, (8,), 8) == 1` — la tabla `(8,)` extrae el LSB
- La tabla identidad `(1..8)` devuelve el valor intacto
- La tabla invertida `(8..1)` produce el espejo exacto
- IP en su primera posición toma el bit 58, que está en el desplazamiento 64−58=6
- PC-1 anula cualquier valor con un único bit en posición múltiplo de 8

### 5.6 Componentes individuales

S₁(100101₂) = 1000₂ según el enunciado; las esquinas de S₁; que todas las salidas
de las ocho cajas caben en cuatro bits; que cada fila de cada S-box es una
permutación de 0 a 15 (propiedad estructural que detecta errores de
transcripción); la rotación circular de 28 bits incluyendo la vuelta completa; y
que `des_round` deja el R anterior como nuevo L.

---

## 6. Por qué 56 bits ya no son suficientes

El espacio de claves de DES contiene

2⁵⁶ ≈ 7,2 × 10¹⁶ claves

La debilidad **no está en la estructura Feistel ni en las S-boxes**. DES fue
diseñado para resistir criptoanálisis diferencial y lineal, y ambos ataques,
aunque posibles, requieren cantidades de datos poco realistas. El problema es
únicamente la longitud de la clave, que permite búsqueda exhaustiva.

La historia lo confirma:

| Año | Máquina | Costo | Tiempo |
|---|---|---|---|
| 1998 | EFF Deep Crack | US$ 250 000 | 56 horas |
| 2006 | COPACOBANA (FPGA) | US$ 10 000 | ≈ 6,4 días |

En ocho años el costo de un ataque práctico cayó veinticinco veces. Hoy, con GPUs
y hardware dedicado, el margen es mucho menor.

DES fue retirado como estándar en 2005. 3DES lo extendió aplicando el algoritmo
tres veces, pero también está considerado *legacy* y desaconsejado para sistemas
nuevos. El estándar actual es AES, con claves de 128, 192 y 256 bits.

---

## 7. Limitaciones de esta implementación

**Opera sobre un solo bloque.** La librería implementa DES tal como lo define el
estándar: una función de 64 bits a 64 bits. Cifrar mensajes de longitud
arbitraria requiere además un esquema de relleno y un modo de operación (CBC,
CTR), que quedan fuera del alcance de este laboratorio.

Durante el desarrollo se construyó una capa preliminar que troceaba mensajes en
bloques independientes. Ese enfoque corresponde al modo **ECB**, y presenta una
debilidad conocida: bloques de texto plano idénticos producen texto cifrado
idéntico, de modo que los patrones del mensaje sobreviven al cifrado. La capa se
retiró de la entrega final por quedar fuera del alcance, pero el hallazgo se
documenta aquí porque ilustra la diferencia entre un cifrador de bloque y un modo
de operación.

**No se detectan claves débiles.** Existen cuatro claves para las que las 16
subclaves resultan idénticas, y seis pares semi-débiles. La librería no las
rechaza.

**No optimiza el rendimiento.** `permute` recorre la tabla bit a bit. Una
implementación de producción usaría tablas precalculadas o instrucciones SIMD.
Para un ejercicio didáctico, la claridad tiene prioridad.

**No debe usarse para proteger información real**, por las razones de la sección
anterior.

---

## 8. Conclusiones

Se implementó DES completo desde la especificación, validado contra el vector
conocido `133457799BBCDFF1` / `0123456789ABCDEF` → `85E813540F0AB405` y contra
las subclaves k1 y k16 del enunciado.

Tres observaciones del proceso:

**La mayoría de los componentes de DES son la misma operación.** IP, IP⁻¹, E, P,
PC-1 y PC-2 se reducen a una única función de cinco líneas. Reconocerlo temprano
convierte seis tareas en una.

**Los errores más peligrosos son los que no lanzan excepción.** Omitir el
intercambio final, interpretar el bit 1 como LSB, o aplicar P y devolver la
salida de las S-boxes sin permutar, producen resultados del tamaño correcto y
aparentemente plausibles. Sin vectores de prueba conocidos, ninguno de los tres
se detecta.

**La verificación por propiedades estructurales es más eficaz que la comparación
directa.** Comprobar que IP⁻¹ deshace IP, que PC-1 descarta exactamente los
múltiplos de 8, que cada fila de S-box es una permutación de 0 a 15 o que C₁₆ =
C₀ detecta errores de transcripción más rápido y con más fiabilidad que releer
quinientos números.

---

## 9. Referencia

FIPS PUB 46-3, *Data Encryption Standard (DES)*, National Institute of Standards
and Technology, octubre de 1999.

---

**Repositorio:** https://github.com/BR2903/lib_des
