from sqlalchemy.exc import IntegrityError
from app.db.session import db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash


def validate_password_strength(password):
    """
    Возвращает текст ошибки или None, если всё ок.
    """
    if len(password) < 8:
        return "Пароль должен быть не короче 8 символов."

    # Проверка на наличие цифры (метод .isdigit())
    if not any(char.isdigit() for char in password):
        return "Пароль должен содержать хотя бы одну цифру."

    # Проверка на заглавную букву (метод .isupper())
    if not any(char.isupper() for char in password):
        return "Пароль должен содержать хотя бы одну заглавную букву."

    return None


def register_user(username, password):
    # 1. Проверяем сложность пароля
    password_error = validate_password_strength(password)
    if password_error:
        return {"success": False, "message": password_error}

    # 2. Проверяем длину логина (например)
    if len(username) < 3:
        return {"success": False, "message": "Логин слишком короткий."}

    # 3. Дальше идет проверка на уникальность в БД и сохранение...
    if User.query.filter_by(username=username).first():
        return {"success": False, "message": "Такой логин уже существует"}

    password_hash = generate_password_hash(password)
    new_user = User(username=username, password_hash=password_hash)
    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return {"success": False, "message": "Ошибка базы данных"}
    return {"success": True, "message": "Успешно!", "user_id": new_user.id}

def login_user(username, password):
    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        return {"success": True, "user_id": user.id}

    return {"success": False, "message": "Неверный логин или пароль"}

