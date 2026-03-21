from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.wallet.wallet import Wallet
from cryptography.hazmat.primitives import serialization
from config import Config

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    wallet_address = db.Column(db.String(500), unique=True)
    wallet_public_key = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)
        self.create_wallet()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def create_wallet(self):
        wallet = Wallet()
        self.wallet_address = wallet.address
        self.wallet_public_key = wallet.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')

    def get_wallet(self):
        if not self.wallet_address:
            self.create_wallet()
        return Wallet.from_dict({
            "address": self.wallet_address,
            "public_key": self.wallet_public_key
        })

    @property
    def is_super_admin(self):
        name = (getattr(Config, 'SUPER_ADMIN_USERNAME', None) or 'jnaranjo').strip().lower()
        return self.username.strip().lower() == name

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "wallet_address": self.wallet_address,
            "is_active": self.is_active,
            "is_super_admin": self.is_super_admin,
        } 