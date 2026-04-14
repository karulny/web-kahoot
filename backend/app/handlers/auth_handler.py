from flask import Blueprint, request, jsonify, session
from backend.app.services.auth_service import login_user, register_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username, password = data.get('username'), data.get('password')

    if not (username and password):
        return jsonify({"success": False, "message": "Укажите логин и пароль"}), 400

    result = login_user(username, password)
    if result.get("success"):
        session['user_id'] = result['user_id']
        return jsonify(result), 200

    return jsonify(result), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username, password = data.get('username'), data.get('password')

    if not (username and password):
        return jsonify({"success": False, "message": "Укажите логин и пароль"}), 400

    result = register_user(username, password)
    if result.get("success"):
        session['user_id'] = result['user_id']
        return jsonify(result), 201

    return jsonify(result), 400

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True}), 200

@auth_bp.route('/me', methods=['GET'])
def me():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"success": False, "message": "Не авторизован"}), 401
    return jsonify({"success": True, "user_id": user_id}), 200