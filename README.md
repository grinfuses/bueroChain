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

## Instalación Local

1. Clonar el repositorio:
```bash
git clone https://github.com/grinfuses/bueroChain.git
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

6. Iniciar un nodo:
```bash
python run_node.py --port 5000
```

7. Iniciar nodos adicionales:
```bash
python run_node.py --port 5001
python run_node.py --port 5002
```

8. Acceder a la interfaz web:
```
http://localhost:5000
```

## Despliegue en Producción (Ubuntu)

### Requisitos del Servidor

- Ubuntu Server 20.04 o superior
- Acceso root o sudo
- Dominio configurado (opcional, pero recomendado)

### Instalación en Producción

1. Actualizar el sistema:
```bash
sudo apt update && sudo apt upgrade -y
```

2. Instalar dependencias del sistema:
```bash
sudo apt install python3-venv python3-pip nginx git -y
```

3. Crear el directorio de la aplicación:
```bash
sudo mkdir /opt/bueroChain
sudo chown ubuntu:ubuntu /opt/bueroChain
```

4. Clonar el repositorio:
```bash
cd /opt/bueroChain
git clone https://github.com/grinfuses/bueroChain.git .
```

5. Crear y activar el entorno virtual:
```bash
python3 -m venv venv
source venv/bin/activate
```

6. Instalar dependencias:
```bash
pip install -r requirements.txt
```

7. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con los valores de producción
nano .env
```

8. Inicializar la base de datos:
```bash
flask db init
flask db migrate
flask db upgrade
```

9. Configurar el servicio systemd:
```bash
sudo cp buerochain.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start buerochain
sudo systemctl enable buerochain
```

10. Configurar Nginx:
```bash
sudo cp buerochain.nginx /etc/nginx/sites-available/buerochain
sudo ln -s /etc/nginx/sites-available/buerochain /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

11. Configurar el firewall:
```bash
sudo ufw allow 'Nginx Full'
```

### Configuración de Múltiples Nodos

1. Crear servicios systemd adicionales:
```bash
# Copiar el servicio para el nodo 2
sudo cp /etc/systemd/system/buerochain.service /etc/systemd/system/buerochain-node2.service

# Editar el nuevo servicio
sudo nano /etc/systemd/system/buerochain-node2.service
# Cambiar el puerto en ExecStart y el nombre del socket
```

2. Crear configuraciones Nginx adicionales:
```bash
# Copiar la configuración para el nodo 2
sudo cp /etc/nginx/sites-available/buerochain /etc/nginx/sites-available/buerochain-node2

# Editar la nueva configuración
sudo nano /etc/nginx/sites-available/buerochain-node2
# Cambiar el server_name y el socket
```

### Monitoreo y Mantenimiento

1. Ver el estado del servicio:
```bash
sudo systemctl status buerochain
```

2. Ver los logs:
```bash
sudo journalctl -u buerochain
sudo tail -f /var/log/nginx/error.log
```

3. Actualizar la aplicación:
```bash
cd /opt/bueroChain
git pull
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
sudo systemctl restart buerochain
```

### Configuración de SSL/TLS

1. Instalar Certbot:
```bash
sudo apt install certbot python3-certbot-nginx
```

2. Obtener certificado SSL:
```bash
sudo certbot --nginx -d buerochain.tudominio.com
```

### Sistema de Respaldo

1. Crear directorio de backups:
```bash
mkdir /opt/bueroChain/backups
```

2. Crear script de backup:
```bash
nano /opt/bueroChain/backup.sh
```

3. Contenido del script de backup:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
sqlite3 /opt/bueroChain/buerochain.db ".backup '/opt/bueroChain/backups/buerochain_$DATE.db'"
```

4. Hacer el script ejecutable:
```bash
chmod +x /opt/bueroChain/backup.sh
```

5. Configurar backup diario:
```bash
crontab -e
# Agregar la línea:
0 0 * * * /opt/bueroChain/backup.sh
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