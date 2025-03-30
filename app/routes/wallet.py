from flask import Blueprint, jsonify
from flask_login import login_required, current_user

bp = Blueprint('wallet', __name__)

@bp.route('/wallet')
@login_required
def get_wallet():
    return jsonify({
        "address": current_user.wallet_address,
        "balance": current_user.get_wallet().get_balance()
    })

@bp.route('/wallet/transactions')
@login_required
def get_transactions():
    # This would be implemented to fetch transactions from the blockchain
    # where the current user's wallet is involved
    return jsonify({
        "message": "Transaction history endpoint to be implemented"
    }) 