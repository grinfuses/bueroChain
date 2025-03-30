# BueroChain - Sistema de Blockchain

BueroChain es un sistema de blockchain descentralizado que permite la validación de operaciones a través de múltiples nodos y la gestión de carteras de usuarios.

## Características

- Sistema de blockchain descentralizado
- Múltiples nodos para validación de operaciones
- Gestión de carteras de usuarios
- Sistema de autenticación y autorización
- API RESTful para interacción con la blockchain

## Requisitos

- Python 3.8+
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/bueroChain.git
cd bueroChain
```

2. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Unix/macOS
# o
.\venv\Scripts\activate  # En Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. Inicializar la base de datos:
```bash
flask db init
flask db migrate
flask db upgrade
```

## Uso

1. Iniciar un nodo:
```bash
python run_node.py --port 5000
```

2. Iniciar nodos adicionales:
```bash
python run_node.py --port 5001
python run_node.py --port 5002
```

3. Acceder a la interfaz web:
```
http://localhost:5000
```

## Estructura del Proyecto

```
bueroChain/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── routes/
│   ├── blockchain/
│   └── wallet/
├── config.py
├── requirements.txt
└── run_node.py
```

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.