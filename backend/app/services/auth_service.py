from sqlalchemy.exc import IntegrityError
from backend.app.db.session import db
from backend.app.models import User
from werkzeug.security import generate_password_hash, check_password_hash


def validate_password_strength(password):
    rules = [
        (len(password) >= 8, "Пароль должен быть не короче 8 символов."),
        (any(c.isdigit() for c in password), "Нужна хотя бы одна цифра."),
        (any(c.isupper() for c in password), "Нужна хотя бы одна заглавная буква.")
    ]
    for condition, msg in rules:
        if not condition:
            return msg
    return None


def register_user(username, password):
    if (err := validate_password_strength(password)):
        return {"success": False, "message": err}

    if len(username) < 3:
        return {"success": False, "message": "Логин слишком короткий."}

    if User.query.filter_by(username=username).first():
        return {"success": False, "message": "Логин занят"}

    user = User(username=username, password_hash=generate_password_hash(password))
    try:
        db.session.add(user)
        db.session.commit()
        return {"success": True, "user_id": user.id}
    except IntegrityError:
        db.session.rollback()
        return {"success": False, "message": "Ошибка БД"}


def login_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        return {"success": True, "user_id": user.id}
    return {"success": False, "message": "Неверные данные"}
