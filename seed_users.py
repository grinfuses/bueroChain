"""
Crea los 3 usuarios de demo para la clase de blockchain.
Ejecutar una sola vez: python seed_users.py
"""
from app import create_app, db
from app.models.user import User

app = create_app()

USERS = [
    ('admin',    'admin@buero.local',    'admin123'),
    ('jnaranjo', 'jnaranjo@buero.local', 'jnaranjo123'),
    ('dorgaz',   'dorgaz@buero.local',   'dorgaz123'),
]

with app.app_context():
    db.create_all()
    created = 0
    for username, email, password in USERS:
        if User.query.filter_by(username=username).first():
            print(f'  [=] {username} ya existe, omitido.')
        else:
            user = User(username=username, email=email, password=password)
            db.session.add(user)
            created += 1
            print(f'  [+] {username} creado.')
    db.session.commit()
    print(f'\nListo: {created} usuario(s) creado(s).')
    print('\nCredenciales:')
    for u, _, p in USERS:
        print(f'  {u:10} / {p}')
