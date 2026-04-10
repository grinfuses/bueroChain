from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.authz import super_admin_required
from app.user_service import create_user_if_valid

bp = Blueprint('auth', __name__)


def _json_body():
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return None
    return data


@bp.route('/register', methods=['POST'])
def register():
    data = _json_body()
    if data is None:
        return jsonify({"error": "JSON body required"}), 400

    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip()
    password = data.get('password')

    user, err = create_user_if_valid(username, email, password)
    if err:
        return jsonify({"error": err}), 400

    return jsonify(user.to_dict()), 201


@bp.route('/admin/users', methods=['POST'])
@super_admin_required
def admin_create_user():
    data = _json_body()
    if data is None:
        return jsonify({"error": "JSON body required"}), 400

    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip()
    password = data.get('password')
    user, err = create_user_if_valid(username, email, password)
    if err:
        return jsonify({"error": err}), 400
    return jsonify(user.to_dict()), 201


@bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@super_admin_required
def admin_delete_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    if user.id == current_user.id:
        return jsonify({"error": "No puedes borrar tu propio usuario"}), 400
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"Usuario {user.username} eliminado"}), 200


@bp.route('/login', methods=['POST'])
def login():
    data = _json_body()
    if data is None:
        return jsonify({"error": "JSON body required"}), 400

    username = (data.get('username') or '').strip()
    password = data.get('password')
    if not username or password is None or password == '':
        return jsonify({"error": "username and password are required"}), 400

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        login_user(user)
        return jsonify(user.to_dict())
    
    return jsonify({"error": "Invalid username or password"}), 401

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"})

@bp.route('/me')
@login_required
def get_current_user():
    return jsonify(current_user.to_dict()) 