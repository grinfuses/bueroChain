# BueroChain — Documentación Completa

## Índice

1. [Visión general](#1-visión-general)
2. [Arquitectura del sistema](#2-arquitectura-del-sistema)
3. [La blockchain: conceptos implementados](#3-la-blockchain-conceptos-implementados)
4. [Moneda BUERO](#4-moneda-buero)
5. [Sistema NFT](#5-sistema-nft)
6. [Referencia de API](#6-referencia-de-api)
7. [Interfaz web](#7-interfaz-web)
8. [Panel de explicaciones](#8-panel-de-explicaciones)
9. [Modelos de datos](#9-modelos-de-datos)
10. [Configuración avanzada](#10-configuración-avanzada)
11. [Guía de uso en clase](#11-guía-de-uso-en-clase)
12. [Despliegue en servidor](#12-despliegue-en-servidor)

---

## 1. Visión general

BueroChain es una implementación completa y funcional de una blockchain con interfaz web, construida para el aula. No depende de librerías de blockchain externas: todo está implementado desde cero en Python para que los alumnos puedan leer y entender cada línea.

**Qué se puede hacer:**

- Iniciar sesión como uno de tres usuarios de demo
- Ver el saldo de la cartera (calculado a partir de la cadena)
- Enviar BUERO a otros usuarios (queda pendiente hasta que se mine)
- Minar un bloque (Proof of Work) y recibir la recompensa
- Mintear NFTs con coste en BUERO y arte generativo basado en el hash
- Transferir NFTs entre usuarios
- Ver la cadena de bloques entera en tiempo real
- Consultar el panel de explicaciones de cada concepto

---

## 2. Arquitectura del sistema

```
┌─────────────────────────────────────────────────────────────┐
│                        Navegador                            │
│   Bootstrap 5 + Jinja2 + fetch() API calls                 │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP
┌────────────────────────▼────────────────────────────────────┐
│                    Flask (puerto 5000)                       │
│                                                             │
│  Blueprints:                                                │
│  ├── ui.py         → HTML: /, /login, /dashboard, /nfts    │
│  ├── blockchain.py → API: /chain /mine /transaction/new … │
│  ├── nft.py        → API: /nft/mint /nft/transfer …       │
│  ├── wallet.py     → API: /wallet                          │
│  └── auth.py       → API: /api/auth                        │
│                                                             │
│  Servicios:                                                 │
│  ├── Blockchain (singleton en memoria)                      │
│  │   └── Lista de Block + pending_transactions             │
│  └── SQLAlchemy ORM                                         │
│       └── SQLite: users + nfts                              │
└─────────────────────────────────────────────────────────────┘
```

### Datos persistentes vs. en memoria

| Dato | Almacenamiento | Nota |
|---|---|---|
| Usuarios, contraseñas, carteras | SQLite | Persiste entre reinicios |
| NFTs, propietario, metadatos | SQLite | Persiste entre reinicios |
| Cadena de bloques | Memoria RAM | Se reinicia con el proceso |
| Transacciones pendientes | Memoria RAM | Se reinicia con el proceso |

> La cadena vive en memoria de forma intencional: en clase se puede resetear simplemente reiniciando el servicio.

---

## 3. La blockchain: conceptos implementados

### 3.1 Bloque

Cada `Block` contiene:

```python
{
    "index":         int,        # posición en la cadena (0 = génesis)
    "transactions":  list,       # transacciones confirmadas
    "timestamp":     float,      # unix timestamp
    "previous_hash": str,        # hash del bloque anterior (enlace)
    "nonce":         int,        # número que satisface la condición PoW
    "hash":          str         # SHA-256 de todos los campos anteriores
}
```

### 3.2 Hash

El hash de un bloque se calcula con:

```python
hashlib.sha256(json.dumps(block_dict, sort_keys=True).encode()).hexdigest()
```

Cambiar cualquier campo (incluso un espacio) produce un hash completamente diferente. Esto hace la cadena **inmutable**.

### 3.3 Proof of Work

Para añadir un bloque, el servidor incrementa `nonce` hasta que:

```
hash[:DIFFICULTY] == "000…"   (tantos ceros como DIFFICULTY)
```

Con `DIFFICULTY = 3`, el servidor prueba ~4.000 nonces de media. Con `DIFFICULTY = 5`, ~100.000. Esto hace costoso falsificar la cadena.

### 3.4 Encadenamiento

Cada bloque almacena el `hash` del bloque anterior. Si modificas el bloque #3:
- Su hash cambia
- El bloque #4 tiene `previous_hash` incorrecto
- La validación (`/validate`) detecta la rotura

### 3.5 Bloque Génesis

El bloque #0 se crea al arrancar el servidor. Su `previous_hash` es `"0"` (convención). El bloque génesis de Bitcoin real lleva el mensaje oculto: `"Chancellor on brink of second bailout for banks"` (3 enero 2009, Satoshi Nakamoto).

---

## 4. Moneda BUERO

### Emisión

La única forma de crear BUERO nuevos es **minar un bloque**. El minero recibe una transacción especial:

```json
{ "from": "network", "to": "<miner_address>", "amount": 10 }
```

Esto replica el modelo de Bitcoin: la oferta monetaria crece solo a través de la minería.

### Cálculo del saldo

El balance **no se almacena** en ninguna tabla. Se calcula en cada consulta recorriendo toda la cadena:

```python
balance = 0
for block in chain:
    for tx in block.transactions:
        if tx["from"] == address: balance -= tx["amount"]
        if tx["to"]   == address: balance += tx["amount"]
# También incluye pending_transactions
```

Esto ilustra el modelo **UTXO-like** de Bitcoin (aunque simplificado).

### Flujo de una transferencia

```
1. Usuario A envía 5 BUERO a B
      → POST /transaction/new
      → blockchain.pending_transactions += [{from: A, to: B, amount: 5}]
      → Saldo de A ya refleja el descuento (incluyendo pendientes)

2. Cualquier usuario mina un bloque
      → GET /mine
      → Se crea un Block con todas las transacciones pendientes
      → El bloque se añade a la cadena (PoW)
      → Transacción confirmada para siempre

3. La recompensa queda pendiente para el siguiente bloque
      → pending_transactions = [{from: "network", to: miner, amount: 10}]
```

---

## 5. Sistema NFT

### ¿Qué es un NFT?

Un NFT (Non-Fungible Token) es un token **único e irrepetible** asociado a un activo digital. A diferencia de los BUERO (fungibles: 1 BUERO = 1 BUERO), cada NFT es distinto y tiene un identificador único.

### Identificador del token

Cuando se mintea un NFT, se genera un `token_id` único:

```python
token_id = SHA256(name + owner_address + timestamp)
```

Este hash de 64 caracteres hexadecimales identifica el NFT de forma global e irrepetible.

### Arte generativo

Cada NFT tiene un arte visual generado automáticamente a partir de su `token_id`:

```javascript
// Los primeros 18 caracteres del hash → 3 colores CSS
c1    = '#' + token_id.substring(0, 6)
c2    = '#' + token_id.substring(6, 12)
c3    = '#' + token_id.substring(12, 18)
angle = parseInt(token_id.substring(18, 20), 16) % 360

// Gradiente único por NFT
gradient = `linear-gradient(${angle}deg, ${c1}, ${c2}, ${c3})`
```

Sobre el gradiente se superpone un overlay SVG con círculos cuyas posiciones y radios también se derivan del hash. Resultado: **ningún NFT puede tener el mismo aspecto**.

### Minteo

- Coste: **5 BUERO** (configurable en `NFT.MINT_FEE`)
- El NFT se guarda inmediatamente en SQLite
- La tarifa genera una transacción `usuario → nft_contract` en la mempool
- El NFT aparece en la galería al instante; la transacción se confirma al minar

### Transferencia

- Actualiza `owner_address` en SQLite instantáneamente
- No requiere BUERO
- El historial de transferencias no se almacena en la cadena (limitación educativa)

### Tabla SQLite `nfts`

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | INTEGER PK | Auto-incremental |
| `token_id` | TEXT UNIQUE | SHA-256 del NFT |
| `name` | TEXT | Nombre del NFT (máx 100 chars) |
| `description` | TEXT | Descripción opcional (máx 300 chars) |
| `owner_address` | TEXT | Dirección actual del propietario |
| `creator_address` | TEXT | Dirección del creador original |
| `created_at` | REAL | Unix timestamp de creación |

---

## 6. Referencia de API

Todas las rutas devuelven JSON. Las marcadas con 🔒 requieren sesión activa (cookie).

### Blockchain

#### `GET /chain`
Devuelve la cadena completa y las transacciones pendientes.

```json
{
  "chain": [
    {
      "index": 0,
      "transactions": [],
      "timestamp": 1708000000.0,
      "previous_hash": "0",
      "nonce": 1234,
      "hash": "000a3f..."
    }
  ],
  "pending_transactions": [],
  "difficulty": 3,
  "mining_reward": 10
}
```

#### `GET /mine` 🔒
Mina el bloque con las transacciones pendientes. El usuario autenticado recibe la recompensa.

```json
{ "message": "Block mined successfully", "reward": 10 }
```

Errores: `500` si la cadena está vacía.

#### `POST /transaction/new` 🔒
Crea una transacción pendiente.

Request:
```json
{ "recipient": "<wallet_address>", "amount": 5.0 }
```

Response:
```json
{
  "message": "Transaction added successfully",
  "transaction": { "from": "...", "to": "...", "amount": 5.0 }
}
```

Errores: `400` (campo faltante, amount <= 0, saldo insuficiente), `404` (destinatario no existe).

#### `GET /balance/<address>`
Devuelve el saldo de una dirección (incluye transacciones pendientes).

```json
{ "address": "...", "balance": 42.5 }
```

#### `GET /validate`
Valida la integridad de la cadena.

```json
{ "is_valid": true }
```

---

### NFT

#### `POST /nft/mint` 🔒
Mintea un nuevo NFT.

Request:
```json
{ "name": "Mi NFT", "description": "Descripción opcional" }
```

Response:
```json
{ "message": "NFT minteado con éxito", "token_id": "abc123..." }
```

Errores: `400` (sin nombre, nombre muy largo, saldo insuficiente).

#### `POST /nft/transfer` 🔒
Transfiere la propiedad de un NFT.

Request:
```json
{ "token_id": "abc123...", "recipient": "<wallet_address>" }
```

Response:
```json
{ "message": "NFT transferido a jnaranjo" }
```

Errores: `403` (no eres el propietario), `404` (NFT o destinatario no existe), `400` (auto-transferencia).

#### `GET /nfts/data` 🔒
Lista todos los NFTs con información del propietario.

```json
[
  {
    "token_id": "abc123...",
    "name": "Mi NFT",
    "description": "...",
    "owner_address": "...",
    "owner_name": "jnaranjo",
    "creator_address": "...",
    "creator_name": "admin",
    "created_at": 1708000000.0,
    "is_mine": true
  }
]
```

---

## 7. Interfaz web

### Dashboard (`/dashboard`)

| Sección | Función |
|---|---|
| Stats bar | Bloques, pendientes, total txs, dificultad — actualización automática |
| Mi Cartera | Balance con animación pulse al recibir, dirección de cartera |
| Enviar BUERO | Selector de destinatario + cantidad, validación de saldo |
| Minería | Hash objetivo, recompensa, botón con animación de hash durante el minado |
| Transacciones Pendientes | Mempool en tiempo real con tipos de transacción |
| Cadena de Bloques | Visualización horizontal scrollable, hover con elevación |

Auto-refresh: `setInterval(loadAll, 6000)` — cada 6 segundos.

### Galería NFT (`/nfts`)

| Sección | Función |
|---|---|
| Stats bar | Total NFTs, mis NFTs, coste de minteo |
| Grid de cards | Arte generativo, nombre, descripción, propietario, botón de transferir |
| Modal Mintear | Preview del arte en tiempo real, validación, coste BUERO |
| Modal Transferir | Preview del NFT seleccionado, selector de destinatario |

---

## 8. Panel de explicaciones

Accesible desde el botón **Explicación** en el navbar. Panel lateral (offcanvas) con secciones independientes:

| Sección | Concepto clave |
|---|---|
| Blockchain | Inmutabilidad — encadenamiento de bloques |
| Hash (SHA-256) | Función determinista y unidireccional |
| Proof of Work | Coste computacional = seguridad |
| Cartera y Dirección | Dirección pública, saldo calculado (no almacenado) |
| Transacciones y Mempool | Confirmaciones, emisión de moneda |
| Bloque Génesis | Origen inmutable, curiosidad Bitcoin |

---

## 9. Modelos de datos

### User

```python
id              INTEGER PK
username        TEXT UNIQUE
email           TEXT UNIQUE
password_hash   TEXT               # werkzeug generate_password_hash
wallet_address  TEXT UNIQUE        # clave pública codificada en base64 (long)
wallet_public_key TEXT             # PEM format
is_active       BOOLEAN
```

La `wallet_address` no es un UUID sino la clave pública codificada, lo que hace las direcciones muy largas (estilo técnico real).

### NFT

Ver sección [5. Sistema NFT → Tabla SQLite](#tabla-sqlite-nfts).

---

## 10. Configuración avanzada

### Variables de entorno (`.env`)

```env
SECRET_KEY=cambia-esto-en-produccion
DATABASE_URL=sqlite:///buerochain.db
NODE_PORT=5000
NODES=                              # IPs de otros nodos separadas por coma
```

### Parámetros de blockchain (`config.py`)

```python
DIFFICULTY    = 3    # 1-5 recomendado para clase; 4+ puede tardar segundos
BLOCK_REWARD  = 10   # BUERO por bloque; cambiar para demostrar inflación/deflación
MINING_TIMEOUT = 30  # segundos máximos de minado (no implementado actualmente)
```

### Restablecer la blockchain

La cadena vive en RAM. Para resetearla:

```bash
sudo systemctl restart buerochain
```

Para resetear también los usuarios y NFTs (BD completa):

```bash
rm /opt/bueroChain/bueroChain/instance/buerochain.db
sudo systemctl restart buerochain
source /opt/bueroChain/bueroChain/venv/bin/activate
python /opt/bueroChain/bueroChain/seed_users.py
```

---

## 11. Guía de uso en clase

### Ejercicio 1 — Introducción (15 min)

1. El profesor inicia sesión como `admin` y proyecta el dashboard.
2. Explica los conceptos del bloque génesis con el panel lateral.
3. Cada alumno inicia sesión con `jnaranjo` o `dorgaz` en su dispositivo.
4. Observan que todos ven la misma cadena (compartida en el servidor).

### Ejercicio 2 — Primera transacción (10 min)

1. `admin` mina el primer bloque → recibe 10 BUERO (recompensa de red).
2. `admin` envía 3 BUERO a `jnaranjo`.
3. Mostrar: la transacción aparece en la mempool (naranja) pero el saldo no cambia en la cadena aún.
4. `jnaranjo` (o cualquier otro) mina un bloque → la transacción se confirma.
5. Observar cómo el bloque recién minado aparece en la cadena.

### Ejercicio 3 — Proof of Work (10 min)

1. Cambiar `DIFFICULTY = 1` → minar instantáneo.
2. Cambiar `DIFFICULTY = 4` → minar tarda unos segundos.
3. Discutir: ¿por qué Bitcoin usa dificultad 22+?

### Ejercicio 4 — Inmutabilidad (10 min)

1. Abrir `/validate` → `true`.
2. Explicar qué pasaría si alguien modificara un bloque antiguo.
3. Mostrar el hash anterior en cada bloque y cómo conectan.

### Ejercicio 5 — NFTs (15 min)

1. `admin` mintea un NFT con su nombre → coste 5 BUERO (pendiente).
2. Mostrar que el arte es único generado por el hash del token.
3. Minar para confirmar la tarifa.
4. Transferir el NFT a `jnaranjo`.
5. Discutir: ¿en qué se diferencia de una imagen JPEG normal?

---

## 12. Despliegue en servidor

### Servicio systemd

Fichero: `/etc/systemd/system/buerochain.service`

```ini
[Unit]
Description=BueroChain - Blockchain Educativa
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/opt/bueroChain/bueroChain
ExecStart=/opt/bueroChain/bueroChain/venv/bin/python run_node.py --port 5000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Firewall (UFW)

```bash
sudo ufw allow 5000/tcp    # acceso directo
sudo ufw status
```

### Requisitos del servidor

- Ubuntu 22.04+ / Debian 11+
- Python 3.10+
- ~512 MB RAM (uso real ~50 MB)
- ~100 MB disco

### Acceso desde la red local (aula)

Compartir la IP del servidor con los alumnos:

```bash
ip addr show | grep 'inet ' | grep -v '127.0'
# Ejemplo: http://192.168.1.100:5000
```

Todos los alumnos se conectan al **mismo servidor** y comparten la misma blockchain. Las transacciones y bloques son visibles para todos en tiempo real.
