from flask import Blueprint, request, jsonify, current_app as app
from backend.app.services.auth_service import login_user, register_user
from backend.app.middlwares.auth import login_required
import jwt
from datetime import datetime, timedelta, timezone

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username, password = data.get('username'), data.get('password')

    if not (username and password):
        return jsonify({"success": False, "message": "Укажите логин и пароль"}), 400

    result = login_user(username, password)
    if result.get("success"):
        token = jwt.encode(
            {
                "user_id": result['user_id'],
                "exp": datetime.now(timezone.utc) + timedelta(days=7)
            },
            app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        return jsonify({"success": True, "token": token}), 200

    return jsonify(result), 401


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username, password = data.get('username'), data.get('password')

    if not (username and password):
        return jsonify({"success": False, "message": "Укажите логин и пароль"}), 400

    result = register_user(username, password)
    if result.get("success"):
        token = jwt.encode(
            {"user_id": result['user_id']},
            app.config['SECRET_KEY'],
            algorithm="HS256"
        )
        return jsonify({"success": True, "token": token}), 201

    return jsonify(result), 400


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    return jsonify({"success": True, "message": "Выход выполнен"}), 200


@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    return jsonify({"success": True, "user_id": request.user_id}), 200
