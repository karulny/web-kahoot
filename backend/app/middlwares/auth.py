from functools import wraps
from flask import session, jsonify, request, current_app as app
import jwt

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({"success": False, "message": "Сначала войдите в систему"}), 401
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            request.user_id = payload["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Время токена истекло"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Неправильный токен"}), 401
        return f(*args, **kwargs)
    return decorated_function