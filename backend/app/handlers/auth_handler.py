from flask import Blueprint, request, jsonify, session
from backend.app.services.auth_service import login_user, register_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    username = data.get('username')
    password = data.get('password')

    result = login_user(username, password)

    if result.get("success"):
        session['user_id'] = result['user_id']  # Сессия все еще работает!
        return jsonify({
            "success": True,
            "message": "Login successful",
            "user_id": result['user_id']
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": result.get("message", "Invalid credentials")
        }), 401


@auth_bp.route("/register", methods=["GET", "POST"])
def register_page():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    result = register_user(username, password)

    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    if result.get("success"):
        session['user_id'] = result['user_id']  # Сессия все еще работает!
        return jsonify({
            "success": True,
            "message": "Login successful",
            "user_id": result['user_id']
        }), 200
    else:
        return jsonify({
            "success": False,
            "message": result.get("message", "Invalid credentials")
        }), 401
