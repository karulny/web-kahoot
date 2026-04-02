from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from app.services.auth_service import register_user, login_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "GET":

        return render_template("login.html")

    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Вызываем сервис
        result = login_user(username, password)

        if result["success"]:
            # 1. Запоминаем пользователя (Бейджик)
            session['user_id'] = result.get('user_id')
            print(session['user_id'])
            # 2. Отправляем на главную
            # return redirect(url_for('index'))
            return render_template("suck.html")
        else:
            # 3. Возвращаем на страницу входа с текстом ошибки
            return render_template("login.html", error=result["message"])



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
            # 1. Запоминаем пользователя (Бейджик)
            session['user_id'] = result.get('user_id')
            # 2. Отправляем на главную
            # return redirect(url_for('index'))
            return render_template("suck.html")
        else:
            # 3. Возвращаем на страницу входа с текстом ошибки
            return render_template("register.html", error=result["message"])