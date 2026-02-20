import json
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.models.nft import NFT
from app.routes.blockchain import blockchain
from config import Config

bp = Blueprint('ui', __name__)


@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('ui.dashboard'))
    return redirect(url_for('ui.login'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('ui.dashboard'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('ui.dashboard'))
        error = 'Usuario o contraseña incorrectos'

    return render_template('login.html', error=error)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('ui.login'))


@bp.route('/dashboard')
@login_required
def dashboard():
    other_users = User.query.filter(User.id != current_user.id).all()
    all_users   = User.query.all()
    all_users_json = json.dumps([
        {'username': u.username, 'wallet_address': u.wallet_address}
        for u in all_users
    ])
    return render_template(
        'dashboard.html',
        other_users=other_users,
        all_users_json=all_users_json,
        mining_reward=blockchain.mining_reward,
        difficulty_zeros='0' * Config.DIFFICULTY,
    )


@bp.route('/nfts')
@login_required
def nfts():
    all_users  = User.query.all()
    user_map   = {u.wallet_address: u.username for u in all_users}
    other_users = User.query.filter(User.id != current_user.id).all()
    return render_template(
        'nfts.html',
        user_map=user_map,
        other_users=other_users,
        mint_fee=NFT.MINT_FEE,
    )


@bp.route('/sepolia')
@login_required
def sepolia():
    return render_template('sepolia.html')
