from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.blockchain.blockchain import Blockchain
from app import db
from app.models.user import User
from config import Config

bp = Blueprint('blockchain', __name__)
blockchain = Blockchain(difficulty=Config.DIFFICULTY)

@bp.route('/chain')
def get_chain():
    return jsonify(blockchain.to_dict())

@bp.route('/mine')
@login_required
def mine():
    blockchain.mine_pending_transactions(current_user.wallet_address)
    return jsonify({
        "message": "Block mined successfully",
        "reward": blockchain.mining_reward
    })

@bp.route('/transaction/new', methods=['POST'])
@login_required
def new_transaction():
    data = request.get_json()
    
    if not all(k in data for k in ['recipient', 'amount']):
        return jsonify({"error": "Missing required fields"}), 400
        
    recipient = User.query.filter_by(wallet_address=data['recipient']).first()
    if not recipient:
        return jsonify({"error": "Recipient not found"}), 404
        
    amount = float(data['amount'])
    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400
        
    if blockchain.get_balance(current_user.wallet_address) < amount:
        return jsonify({"error": "Insufficient funds"}), 400
        
    blockchain.add_transaction(
        current_user.wallet_address,
        recipient.wallet_address,
        amount
    )
    
    return jsonify({
        "message": "Transaction added successfully",
        "transaction": {
            "from": current_user.wallet_address,
            "to": recipient.wallet_address,
            "amount": amount
        }
    })

@bp.route('/balance/<address>')
def get_balance(address):
    balance = blockchain.get_balance(address)
    return jsonify({
        "address": address,
        "balance": balance
    })

@bp.route('/validate')
def validate_chain():
    is_valid = blockchain.is_chain_valid()
    return jsonify({
        "is_valid": is_valid
    }) 