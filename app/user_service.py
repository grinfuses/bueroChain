from app import db
from app.models.user import User


def create_user_if_valid(username, email, password):
    """
    Crea un usuario si los datos son válidos y únicos.
    Devuelve (user, None) si OK, o (None, mensaje_error) en inglés (API).
    """
    username = (username or '').strip()
    email = (email or '').strip()
    if not username or not email:
        return None, 'username and email are required'
    if password is None or password == '':
        return None, 'password is required'
    if User.query.filter_by(username=username).first():
        return None, 'Username already exists'
    if User.query.filter_by(email=email).first():
        return None, 'Email already exists'
    user = User(username=username, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return user, None
