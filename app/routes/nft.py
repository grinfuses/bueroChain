import os
import time
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models.nft import NFT
from app.models.user import User
from app.routes.blockchain import blockchain

bp = Blueprint('nft', __name__)

# Special burn address for mint fees — appears on the blockchain as "NFT Contract"
NFT_CONTRACT = 'nft_contract'


def _allowed_file(filename):
    return ('.' in filename and
            filename.rsplit('.', 1)[1].lower() in NFT.ALLOWED_EXTENSIONS)


def _save_image(file, token_id):
    """Save uploaded image and return the stored filename, or None on failure."""
    if not file or file.filename == '':
        return None
    if not _allowed_file(file.filename):
        return None
    ext = secure_filename(file.filename).rsplit('.', 1)[1].lower()
    filename = f"{token_id}.{ext}"
    upload_dir = os.path.join(current_app.root_path, 'static', 'nft_images')
    os.makedirs(upload_dir, exist_ok=True)
    file.save(os.path.join(upload_dir, filename))
    return filename


@bp.route('/nft/mint', methods=['POST'])
@login_required
def mint_nft():
    # Accept both multipart/form-data (with image) and application/json
    if request.content_type and 'multipart/form-data' in request.content_type:
        name        = (request.form.get('name') or '').strip()
        description = (request.form.get('description') or '').strip()
        image_file  = request.files.get('image')
    else:
        data        = request.get_json() or {}
        name        = data.get('name', '').strip()
        description = data.get('description', '').strip()
        image_file  = None

    if not name:
        return jsonify({'error': 'El nombre es obligatorio'}), 400
    if len(name) > 100:
        return jsonify({'error': 'Nombre demasiado largo (máx. 100 caracteres)'}), 400
    if len(description) > 300:
        return jsonify({'error': 'Descripción demasiado larga (máx. 300 caracteres)'}), 400

    balance = blockchain.get_balance(current_user.wallet_address)
    if balance < NFT.MINT_FEE:
        return jsonify({
            'error': f'Saldo insuficiente. Necesitas {NFT.MINT_FEE} BUERO para mintear un NFT '
                     f'(tienes {balance:.2f} BUERO)'
        }), 400

    ts       = time.time()
    token_id = NFT.generate_token_id(name, current_user.wallet_address, ts)

    # Save image if provided
    image_filename = _save_image(image_file, token_id) if image_file else None

    nft = NFT(
        token_id=token_id,
        name=name,
        description=description,
        owner_address=current_user.wallet_address,
        creator_address=current_user.wallet_address,
        created_at=ts,
        image_filename=image_filename,
    )
    db.session.add(nft)

    # Register the mint fee on the blockchain (pending, needs mining)
    blockchain.add_transaction(
        sender=current_user.wallet_address,
        recipient=NFT_CONTRACT,
        amount=NFT.MINT_FEE,
    )

    db.session.commit()
    return jsonify({'message': 'NFT minteado con éxito', 'token_id': token_id})


@bp.route('/nft/transfer', methods=['POST'])
@login_required
def transfer_nft():
    data              = request.get_json() or {}
    token_id          = data.get('token_id', '')
    recipient_address = data.get('recipient', '')

    nft = NFT.query.filter_by(token_id=token_id).first()
    if not nft:
        return jsonify({'error': 'NFT no encontrado'}), 404
    if nft.owner_address != current_user.wallet_address:
        return jsonify({'error': 'No eres el propietario de este NFT'}), 403

    recipient = User.query.filter_by(wallet_address=recipient_address).first()
    if not recipient:
        return jsonify({'error': 'Destinatario no encontrado'}), 404
    if recipient_address == current_user.wallet_address:
        return jsonify({'error': 'No puedes transferirte un NFT a ti mismo'}), 400

    nft.owner_address = recipient_address
    db.session.commit()
    return jsonify({'message': f'NFT transferido a {recipient.username}'})


@bp.route('/nfts/data')
@login_required
def nfts_data():
    """JSON endpoint used by the gallery to refresh without full page reload."""
    all_users = User.query.all()
    user_map  = {u.wallet_address: u.username for u in all_users}

    nfts = NFT.query.order_by(NFT.created_at.desc()).all()
    return jsonify([{
        'token_id':        n.token_id,
        'name':            n.name,
        'description':     n.description,
        'owner_address':   n.owner_address,
        'owner_name':      user_map.get(n.owner_address, n.owner_address[:10] + '…'),
        'creator_address': n.creator_address,
        'creator_name':    user_map.get(n.creator_address, n.creator_address[:10] + '…'),
        'created_at':      n.created_at,
        'is_mine':         n.owner_address == current_user.wallet_address,
        'image_url':       f'/static/nft_images/{n.image_filename}' if n.image_filename else None,
    } for n in nfts])
