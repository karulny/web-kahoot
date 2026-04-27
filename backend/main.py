import os
from flask import Flask, render_template, session, redirect, url_for
from flask_cors import CORS
from backend.app.db.session import db
from backend.app.handlers.auth_handler import auth_bp
from backend.app.handlers.quiz_handler import quiz_bp
from backend.app.handlers.game_handler import game_bp

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
CORS(app, supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'SQLALCHEMY_DATABASE_URI',
    'postgresql://postgres:1111@localhost:5432/quiz_db'
)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db.init_app(app)

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(quiz_bp, url_prefix='/quiz')
app.register_blueprint(game_bp, url_prefix='/game')

with app.app_context():
    db.create_all()


@app.route('/')
def index():
    ...


@app.route('/auth')
def auth_page():
    ...


@app.route('/dashboard')
def dashboard():
    ...


@app.route('/host/<int:session_id>/<pin>')
def host_page():
    ...


@app.route('/play/<pin>')
def play_page():
    ...


if __name__ == '__main__':
    app.run(debug=True)
