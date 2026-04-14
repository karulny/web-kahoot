from flask import Flask
from backend.app.db.session import db
from backend.app.handlers.auth_handler import auth_bp
from backend.app.handlers.quiz_handler import quiz_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1111@localhost:5432/quiz_db'
app.config['SECRET_KEY'] = 'super-secret-key'

db.init_app(app)

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(quiz_bp, url_prefix='/quiz')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
