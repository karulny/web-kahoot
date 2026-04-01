from flask import Flask
from app.db.session import db
from app.handlers.quiz_handler import quiz_bp

app = Flask(__name__,
            template_folder='app/templates',
            static_folder='app/static')

# Настройки
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1111@localhost:5432/quiz_db'
app.config['SECRET_KEY'] = 'super-secret-key'

# Инициализация БД
db.init_app(app)

# Регистрация хэндлеров (Blueprint)
app.register_blueprint(quiz_bp, url_prefix='/quiz')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)