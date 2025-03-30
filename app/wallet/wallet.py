from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import base64
import json

class Wallet:
    def __init__(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        self.address = self.generate_address()

    def generate_address(self):
        public_key_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return base64.b64encode(public_key_bytes).decode('utf-8')

    def sign_transaction(self, transaction):
        transaction_string = json.dumps(transaction, sort_keys=True)
        signature = self.private_key.sign(
            transaction_string.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')

    def verify_transaction(self, transaction, signature):
        try:
            self.public_key.verify(
                base64.b64decode(signature),
                json.dumps(transaction, sort_keys=True).encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except:
            return False

    def to_dict(self):
        return {
            "address": self.address,
            "public_key": self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8')
        }

    @staticmethod
    def from_dict(wallet_dict):
        wallet = Wallet()
        wallet.address = wallet_dict["address"]
        wallet.public_key = serialization.load_pem_public_key(
            wallet_dict["public_key"].encode(),
            backend=default_backend()
        )
        return wallet 