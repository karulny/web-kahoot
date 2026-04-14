from flask import Blueprint, request, jsonify, session
from backend.app.services.auth_service import login_user, register_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Нет данных"}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Укажите логин и пароль"}), 400

    result = login_user(username, password)

    if result.get("success"):
        session['user_id'] = result['user_id']
        return jsonify({"success": True, "user_id": result['user_id']}), 200

    return jsonify({"success": False, "message": result.get("message")}), 401


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Нет данных"}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Укажите логин и пароль"}), 400

    result = register_user(username, password)

    if result.get("success"):
        session['user_id'] = result['user_id']
        return jsonify({"success": True, "user_id": result['user_id']}), 201

    return jsonify({"success": False, "message": result.get("message")}), 400


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True}), 200


@auth_bp.route('/me', methods=['GET'])
def me():
    """Проверка текущей сессии"""
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Не авторизован"}), 401
    return jsonify({"success": True, "user_id": session['user_id']}), 200
