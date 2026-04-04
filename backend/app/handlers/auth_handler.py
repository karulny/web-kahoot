from flask import Blueprint, request, session, jsonify
from backend.app.services.auth_service import register_user, login_user

auth_bp = Blueprint('auth', __name__)

auth_bp.route("/login", methods=["POST"])
def login_api():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    result = login_user(username, password)

    if result["success"]:
        session['user_id'] = result['user_id']
        return jsonify({"success": True, "message": "Вход выполнен"}), 200
    else:
        return jsonify({"success": False, "message": result["message"]}), 401



@auth_bp.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "GET":

        return render_template("register.html")

    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Вызываем сервис
        result = register_user(username, password)

        if result["success"]:
            session['user_id'] = result['user_id']
            return jsonify({"success": True, "message": "Вход выполнен"}), 200
        else:
            return jsonify({"success": False, "message": result["message"]}), 401