# AGENTS.md — Guía para agentes de IA (Claude Code / Copilot / etc.)

Este fichero describe las convenciones, arquitectura y reglas del proyecto **BueroChain** para que un agente de IA pueda trabajar en él con contexto completo.

---

## Propósito del proyecto

BueroChain es una **blockchain educativa** en Flask (Python). El objetivo es la legibilidad y la experiencia de clase, no el rendimiento ni la seguridad de producción. Las decisiones de diseño priorizan la simplicidad didáctica.

---

## Stack técnico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.x · Flask · SQLAlchemy · Flask-Login · Flask-Migrate |
| Base de datos | SQLite (fichero `instance/buerochain.db`) |
| Frontend | Jinja2 · Bootstrap 5.3 · Font Awesome 6 · Inter · JetBrains Mono |
| Blockchain | Implementación propia en Python (sin librerías externas de blockchain) |
| Proceso | systemd service `buerochain` · puerto 5000 |

---

## Arquitectura de ficheros clave

```
app/__init__.py          → create_app() — registra blueprints
app/blockchain/
  block.py               → Block(index, transactions, timestamp, previous_hash)
  blockchain.py          → Blockchain singleton (módulo-nivel en routes/blockchain.py)
app/models/
  user.py                → User(username, email, password) — crea cartera al init
  nft.py                 → NFT(token_id, name, description, owner_address, …)
app/routes/
  ui.py                  → rutas HTML: /, /login, /logout, /dashboard, /nfts
  blockchain.py          → API JSON: /chain /mine /transaction/new /balance /validate
  nft.py                 → API JSON: /nft/mint /nft/transfer /nfts/data
  wallet.py              → API JSON: /wallet /wallet/transactions
  auth.py                → API JSON: /api/auth (con prefijo /api)
app/templates/
  base.html              → layout, navbar, offcanvas de explicaciones, CSS variables
  login.html             → formulario de login
  dashboard.html         → cartera + enviar + minería + mempool + cadena de bloques
  nfts.html              → galería NFT + modales mint/transfer
config.py                → DIFFICULTY, BLOCK_REWARD, SECRET_KEY, DATABASE_URL
```

---

## Convenciones de código

### Python
- Blueprints: cada fichero de `routes/` expone `bp = Blueprint(...)`.
- El objeto `blockchain` (instancia de `Blockchain`) vive en `app/routes/blockchain.py` a nivel de módulo. Para usarlo en otros blueprints, importar con `from app.routes.blockchain import blockchain`.
- Los modelos SQLAlchemy usan `db` de `app/__init__.py`.
- Flask-Login: `@login_required` en todas las rutas que necesitan autenticación.
- Errores API: siempre devolver `jsonify({'error': '...'})` con código HTTP apropiado.
- No usar `flask db migrate` en producción: la BD se crea con `db.create_all()` en `run_node.py`.

### Jinja2 / HTML
- Todos los templates extienden `base.html`.
- Las variables CSS están en `:root` dentro de `base.html` (`--bg-base`, `--blue`, `--green`, etc.).
- Usar las clases utilitarias definidas en `base.html` (`.hash-text`, `.nft-art`, `.stat-card`, `.btn-mine`, etc.) antes de añadir estilos inline.
- JavaScript de cada página va en `{% block scripts %}`.
- Las llamadas a la API desde el frontend son `fetch()` asíncronas sin frameworks adicionales.

### CSS
- Paleta de colores definida en variables CSS en `base.html`:
  ```css
  --bg-base, --bg-card, --bg-card2, --bg-input
  --border, --border-hi
  --text-main, --text-muted
  --blue, --green, --orange, --red, --yellow, --purple
  --blue-glow, --green-glow, --orange-glow
  ```
- Tipografías: `Inter` (texto general) y `JetBrains Mono` (hashes, valores numéricos).
- No añadir librerías CSS externas adicionales sin consultarlo.

---

## Flujo de datos principal

```
Usuario hace login
  └─ Flask-Login → session cookie

Usuario envía BUERO
  └─ POST /transaction/new
       └─ blockchain.add_transaction(from, to, amount)
            └─ añade a blockchain.pending_transactions

Usuario mina bloque
  └─ GET /mine
       └─ blockchain.mine_pending_transactions(miner_address)
            └─ crea Block, calcula PoW, añade a chain
            └─ pending_transactions = [recompensa de red]

Usuario mintea NFT
  └─ POST /nft/mint
       └─ comprueba balance >= 5 BUERO
       └─ NFT guardado en SQLite (inmediato)
       └─ blockchain.add_transaction(user, 'nft_contract', 5.0) [pendiente]
```

---

## Reglas importantes para el agente

1. **No reescribir la lógica del blockchain** (`block.py`, `blockchain.py`). Solo modificar si hay un bug explícito.
2. **No borrar usuarios existentes** ni la tabla `users` sin instrucción explícita.
3. **El objeto `blockchain` es un singleton en memoria.** Si el proceso reinicia, la cadena se reinicia. Esto es intencional (uso en clase).
4. **NFT_CONTRACT = `'nft_contract'`** es una dirección especial que no pertenece a ningún User. No añadir validación de User para esta dirección en las rutas blockchain.
5. **El balance incluye transacciones pendientes** (ver `blockchain.get_balance`). Es intencional para mostrar el descuento inmediato al enviar.
6. Al añadir nuevas páginas HTML, seguir el patrón: ruta en `ui.py` + template en `templates/`.
7. Al añadir nuevas rutas API, crear un blueprint nuevo en `routes/` y registrarlo en `__init__.py`.
8. Reiniciar el servicio con `sudo systemctl restart buerochain` después de cambios en Python. No es necesario para cambios solo en templates HTML (Flask los recarga en modo debug, pero en producción sí hay que reiniciar).

---

## Comandos útiles

```bash
# Estado del servicio
sudo systemctl status buerochain

# Logs en tiempo real
sudo journalctl -u buerochain -f

# Reiniciar
sudo systemctl restart buerochain

# Recrear usuarios de demo (borra la BD primero si es necesario)
cd /opt/bueroChain/bueroChain
source venv/bin/activate
python seed_users.py

# Borrar la BD y empezar de cero
rm instance/buerochain.db
python run_node.py --port 5000   # recrea la BD y el bloque génesis
```

---

## Lo que NO hacer

- No añadir autenticación JWT ni OAuth — Flask-Login es suficiente para el contexto educativo.
- No migrar a PostgreSQL — SQLite es intencional.
- No añadir WebSockets para actualizaciones en tiempo real — el polling cada 6 s es suficiente.
- No cambiar el puerto 5000 sin actualizar también el fichero de servicio systemd.
- No hacer `pip install` de nuevas dependencias sin añadirlas a `requirements.txt`.
