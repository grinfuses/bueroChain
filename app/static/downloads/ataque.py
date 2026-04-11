"""
ataque.py — Taller BueroChain
==============================
Este script demuestra por qué una blockchain es inmutable.

Pasos que ejecuta:
  1. Descarga la cadena completa desde el servidor
  2. Muestra un bloque con transacciones reales
  3. Intenta falsificar el importe de una transacción
  4. Recalcula el hash y comprueba que ya no coincide con el registrado
  5. Verifica contra el endpoint /validate del servidor
  6. Vuelve a descargar la cadena y demuestra que el servidor sigue intacto

Requisitos: Python 3.8+ y el módulo 'requests'
  pip install requests

Uso:
  python ataque.py
  python ataque.py --url http://IP_DEL_SERVIDOR:2026
"""

import argparse
import hashlib
import json
import sys

try:
    import requests
except ImportError:
    print("ERROR: Necesitas instalar 'requests'")
    print("  pip install requests")
    sys.exit(1)


# ─── Configuración ────────────────────────────────────────────────────────────

DEFAULT_URL = "http://141.95.55.11:2026"  # Cambia esto o usa --url

SEPARADOR = "─" * 60


# ─── Helpers ──────────────────────────────────────────────────────────────────

def titular(texto):
    print(f"\n{'═' * 60}")
    print(f"  {texto}")
    print(f"{'═' * 60}")


def calcular_hash(bloque: dict) -> str:
    """Replica exactamente la función de BueroChain para calcular el hash."""
    bloque_str = json.dumps(bloque, sort_keys=True).encode()
    return hashlib.sha256(bloque_str).hexdigest()


# ─── Pasos del ataque ─────────────────────────────────────────────────────────

def paso1_descargar_cadena(base_url: str) -> list:
    titular("PASO 1 — Descargar la cadena desde el servidor")

    url = f"{base_url}/chain"
    print(f"  Conectando a: {url}")

    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        print(f"\n  ERROR: No se puede conectar a {base_url}")
        print("  ¿Está el servidor arriba? ¿Es correcta la IP?")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"\n  ERROR HTTP: {e}")
        sys.exit(1)

    data = resp.json()
    cadena = data.get("chain", [])

    print(f"  ✓ Cadena recibida: {len(cadena)} bloque(s)")
    for bloque in cadena:
        txs = bloque.get("transactions", [])
        print(f"    Bloque #{bloque['index']}  —  {len(txs)} transacción(es)  —  hash: {bloque['hash'][:20]}...")

    return cadena


def paso2_elegir_victima(cadena: list) -> tuple:
    titular("PASO 2 — Buscar un bloque con transacciones para falsificar")

    # Buscar el primer bloque (no génesis) con al menos una transacción
    # que tenga un importe numérico real (no solo recompensas de red internas)
    bloque_victima = None
    tx_idx = None

    for bloque in cadena:
        if bloque["index"] == 0:
            continue  # saltar génesis
        for i, tx in enumerate(bloque.get("transactions", [])):
            if tx.get("from") != "network" and isinstance(tx.get("amount"), (int, float)):
                bloque_victima = bloque
                tx_idx = i
                break
        if bloque_victima:
            break

    # Si no hay transacciones de usuario, intentamos con recompensas de red
    if not bloque_victima:
        for bloque in cadena:
            if bloque["index"] == 0:
                continue
            if bloque.get("transactions"):
                bloque_victima = bloque
                tx_idx = 0
                break

    if not bloque_victima:
        print("\n  ⚠ La cadena solo tiene el bloque génesis y no hay transacciones.")
        print("  Haz una transferencia y mina un bloque antes de ejecutar este script.")
        sys.exit(0)

    tx = bloque_victima["transactions"][tx_idx]
    print(f"\n  Bloque seleccionado : #{bloque_victima['index']}")
    print(f"  Hash registrado     : {bloque_victima['hash']}")
    print(f"\n  Transacción a falsificar:")
    print(f"    De      : {tx.get('from', '?')[:40]}...")
    print(f"    Para    : {tx.get('to', '?')[:40]}...")
    print(f"    Importe : {tx['amount']} BUERO")

    return bloque_victima, tx_idx


def paso3_falsificar(bloque_original: dict, tx_idx: int) -> dict:
    titular("PASO 3 — Falsificar el importe de la transacción")

    importe_original = bloque_original["transactions"][tx_idx]["amount"]
    importe_falso    = importe_original * 100  # multiplicamos por 100

    print(f"  Importe original : {importe_original} BUERO")
    print(f"  Importe falso    : {importe_falso} BUERO  (x100)")

    # Construimos una copia del bloque con el dato modificado
    bloque_falso = json.loads(json.dumps(bloque_original))  # deep copy
    bloque_falso["transactions"][tx_idx]["amount"] = importe_falso

    print("\n  Bloque modificado en memoria (el servidor NO sabe nada de esto aún)")
    return bloque_falso


def paso4_recalcular_hash(bloque_original: dict, bloque_falso: dict):
    titular("PASO 4 — Recalcular el hash del bloque falsificado")

    # El hash se calcula sobre todos los campos EXCEPTO el propio 'hash'
    datos_para_hash_original = {k: v for k, v in bloque_original.items() if k != "hash"}
    datos_para_hash_falso    = {k: v for k, v in bloque_falso.items()    if k != "hash"}

    hash_original   = calcular_hash(datos_para_hash_original)
    hash_recalculado = calcular_hash(datos_para_hash_falso)

    print(f"\n  Hash registrado en el bloque  : {hash_original}")
    print(f"  Hash del bloque falsificado   : {hash_recalculado}")

    if hash_original == hash_recalculado:
        print("\n  [???] Los hashes coinciden — esto no debería pasar.")
    else:
        print(f"\n  ✗ LOS HASHES NO COINCIDEN")
        print(f"    Cambiamos un número y el hash cambió por completo.")
        print(f"    SHA-256 es determinista: cualquier cambio mínimo")
        print(f"    produce un hash totalmente diferente.")

    print(f"\n  Diferencia en los primeros caracteres:")
    for i, (a, b) in enumerate(zip(hash_original, hash_recalculado)):
        if a != b:
            print(f"    Posición {i}: '{a}' → '{b}'  (primer carácter distinto)")
            break


def paso5_validar_servidor(base_url: str):
    titular("PASO 5 — Preguntar al servidor si la cadena es válida")

    url = f"{base_url}/validate"
    print(f"  GET {url}")

    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
    except Exception as e:
        print(f"  ERROR al contactar /validate: {e}")
        return

    es_valida = data.get("is_valid", None)

    if es_valida is True:
        print(f"\n  ✓ El servidor responde: cadena VÁLIDA")
        print(f"    (Nuestra falsificación fue local — el servidor no sabe nada)")
        print(f"    Para que el servidor lo aceptara, tendríamos que:")
        print(f"      1. Recalcular el hash del bloque falsificado")
        print(f"      2. Actualizar el previous_hash de TODOS los bloques siguientes")
        print(f"      3. Rehacer el Proof of Work (minar) de CADA uno de esos bloques")
        print(f"      4. Hacerlo más rápido que el resto de la red")
        print(f"    → Eso es el ataque del 51%. Computacionalmente inviable en Bitcoin.")
    else:
        print(f"\n  ✗ El servidor responde: cadena INVÁLIDA")
        print(f"    Alguien ya ha manipulado la cadena en el servidor.")


def paso6_recomprobar_servidor(base_url: str, bloque_original: dict, tx_idx: int, bloque_falso: dict):
    titular("PASO 6 — Volver a pedir la cadena al servidor")

    url = f"{base_url}/chain"
    print(f"  GET {url}")

    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  ERROR al contactar /chain: {e}")
        return

    cadena_actual = data.get("chain", [])

    # Localizamos el mismo bloque por índice
    bloque_servidor = next(
        (b for b in cadena_actual if b["index"] == bloque_original["index"]),
        None
    )

    if bloque_servidor is None:
        print(f"  ⚠ El bloque #{bloque_original['index']} ya no está en la cadena.")
        return

    importe_servidor = bloque_servidor["transactions"][tx_idx]["amount"]
    importe_falso    = bloque_falso["transactions"][tx_idx]["amount"]
    importe_original = bloque_original["transactions"][tx_idx]["amount"]
    hash_servidor    = bloque_servidor["hash"]
    hash_original    = bloque_original["hash"]

    print(f"\n  Lo que tenemos en MEMORIA LOCAL (nuestra falsificación):")
    print(f"    Importe : {importe_falso} BUERO")
    print(f"\n  Lo que tiene el SERVIDOR ahora mismo:")
    print(f"    Importe : {importe_servidor} BUERO")
    print(f"    Hash    : {hash_servidor}")

    if importe_servidor == importe_original and hash_servidor == hash_original:
        print(f"\n  ✓ La cadena del servidor está IDÉNTICA a antes del ataque.")
        print(f"    Importe intacto, hash intacto. Nuestra falsificación")
        print(f"    nunca salió de la RAM de este script.")
        print(f"\n  Moraleja:")
        print(f"    Modificar tu copia local de una blockchain es como")
        print(f"    fotocopiar un billete y tachar un cero más: tu copia")
        print(f"    cambia, pero la realidad de la red no.")
    else:
        print(f"\n  ⚠ Algo ha cambiado en el servidor entre el PASO 1 y ahora.")
        print(f"    Probablemente alguien minó un bloque o hizo una transacción.")


def conclusion():
    titular("CONCLUSIÓN")
    print("""
  ¿Qué hemos aprendido?

  1. Cada bloque tiene un hash que depende de TODO su contenido.
     Cambiar un solo byte → hash completamente diferente.

  2. Cada bloque guarda el hash del bloque anterior (previous_hash).
     Si cambias el bloque #2, el bloque #3 ya no encaja.
     Y el #4 tampoco. Ni el #5. La cadena entera se rompe.

  3. Para "colar" una falsificación necesitarías:
     - Rehacer el Proof of Work de todos los bloques siguientes
     - Ir más rápido que todos los mineros honestos juntos
     → Eso es lo que hace imposible la manipulación en redes grandes.

  4. Lo que hemos hecho aquí (modificar en memoria local) no afecta
     al servidor para nada. La falsificación muere en nuestro script.

  Blockchain no es magia. Es matemática + incentivos económicos.
""")
    print(SEPARADOR)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="BueroChain — Script de ataque educativo")
    parser.add_argument(
        "--url",
        default=DEFAULT_URL,
        help=f"URL base del servidor BueroChain (default: {DEFAULT_URL})"
    )
    args = parser.parse_args()

    base_url = args.url.rstrip("/")

    print(f"\n  BueroChain — Taller de Blockchain")
    print(f"  Servidor: {base_url}")
    print(SEPARADOR)

    cadena                      = paso1_descargar_cadena(base_url)
    bloque_original, tx_idx     = paso2_elegir_victima(cadena)
    bloque_falso                = paso3_falsificar(bloque_original, tx_idx)
    paso4_recalcular_hash(bloque_original, bloque_falso)
    paso5_validar_servidor(base_url)
    paso6_recomprobar_servidor(base_url, bloque_original, tx_idx, bloque_falso)
    conclusion()


if __name__ == "__main__":
    main()
