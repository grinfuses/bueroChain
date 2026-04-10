# BueroChain

Blockchain educativa con interfaz web completa. Incluye minería Proof of Work, transferencias de la moneda BUERO, galería NFT con arte generativo y panel de explicaciones para clase.

> Proyecto diseñado para enseñar los fundamentos de blockchain en un entorno de aula. No usar en producción.

---

## Características

| Módulo | Descripción |
|---|---|
| Blockchain | Cadena de bloques con Proof of Work (SHA-256, dificultad configurable) |
| BUERO | Moneda propia: transferencias entre usuarios, recompensa por minado |
| NFTs | Minteo (coste en BUERO), arte generativo por hash, transferencia |
| Panel educativo | Offcanvas con explicaciones de cada concepto |
| Interfaz web | Dark theme · Bootstrap 5 · Inter + JetBrains Mono |
| 3 usuarios demo | Listos para usar desde `seed_users.py` |

---

## Inicio rápido

```bash
cd /opt/bueroChain/bueroChain
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python seed_users.py       # Crea los 3 usuarios de demo
python run_node.py --port 2026
```

Abre `http://localhost:2026` en el navegador.

---

## Credenciales de demo

Las contraseñas iniciales se definen en [`seed_users.py`](seed_users.py). Cambia los valores antes de lanzar un taller público — el instructor reparte las credenciales en clase.

| Usuario | Rol |
|---|---|
| `admin` | Creador (corona en cartera) |
| `jnaranjo` | Super admin — único con permiso para minar y borrar usuarios |
| `dorgaz` | Alumno |

---

## Servicio systemd (servidor)

```bash
sudo systemctl {start|stop|restart|status} buerochain
sudo journalctl -u buerochain -f          # logs en tiempo real
```

---

## Configuración rápida

Edita `config.py` y reinicia el servicio:

```python
DIFFICULTY   = 3    # ceros requeridos al inicio del hash (+ = más lento)
BLOCK_REWARD = 10   # BUERO que recibe el minero por bloque
```

---

## Estructura

```
bueroChain/
├── app/
│   ├── blockchain/        block.py · blockchain.py
│   ├── models/            user.py · nft.py
│   ├── routes/            ui.py · blockchain.py · nft.py · wallet.py · auth.py
│   ├── templates/         base.html · login.html · dashboard.html · nfts.html
│   └── wallet/            wallet.py
├── config.py
├── run_node.py
├── seed_users.py
├── README.md
├── AGENTS.md
└── DOCS.md
```

---

## Documentación completa

Ver [DOCS.md](DOCS.md) para arquitectura detallada, referencia de API, sistema NFT y guía de uso en clase.
