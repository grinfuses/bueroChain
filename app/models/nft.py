import hashlib
from app import db


class NFT(db.Model):
    __tablename__ = 'nfts'

    id              = db.Column(db.Integer, primary_key=True)
    token_id        = db.Column(db.String(64), unique=True, nullable=False)
    name            = db.Column(db.String(100), nullable=False)
    description     = db.Column(db.String(300), default='')
    owner_address   = db.Column(db.String(500), nullable=False)
    creator_address = db.Column(db.String(500), nullable=False)
    created_at      = db.Column(db.Float, nullable=False)
    image_filename  = db.Column(db.String(200), nullable=True)   # uploaded image, if any

    MINT_FEE = 5.0
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    @staticmethod
    def generate_token_id(name, address, timestamp):
        data = f"{name}{address}{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()
