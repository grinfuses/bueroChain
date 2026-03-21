from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app.routes.blockchain import blockchain

bp = Blueprint('wallet', __name__)

@bp.route('/wallet')
@login_required
def get_wallet():
    return jsonify({
        "address": current_user.wallet_address,
        "balance": blockchain.get_balance(current_user.wallet_address),
    })

@bp.route('/wallet/transactions')
@login_required
def get_transactions():
    # This would be implemented to fetch transactions from the blockchain
    # where the current user's wallet is involved
    return jsonify({
        "message": "Transaction history endpoint to be implemented"
    }) 