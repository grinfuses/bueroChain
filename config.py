import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///buerochain.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Blockchain configuration
    DIFFICULTY = 3  # Number of leading zeros required in block hash (3 = rápido para demo)
    BLOCK_REWARD = 10  # Reward for mining a new block
    MINING_TIMEOUT = 30  # Timeout for mining in seconds
    
    # Node configuration
    NODE_PORT = int(os.environ.get('NODE_PORT', 2026))
    NODES = os.environ.get('NODES', '').split(',')  # List of other nodes in the network

    # Super admin: puede crear usuarios (UI + POST /api/admin/users)
    SUPER_ADMIN_USERNAME = (os.environ.get('SUPER_ADMIN_USERNAME') or 'jnaranjo').strip() 