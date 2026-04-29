import os
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from backend.app.db.session import db
from backend.app.handlers.auth_handler import auth_bp
from backend.app.handlers.quiz_handler import quiz_bp
from backend.app.handlers.game_handler import game_bp

app = Flask(
    __name__,
    template_folder='../frontend/templates',
    static_folder='../frontend/static'
)
CORS(app, supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'SQLALCHEMY_DATABASE_URI',
    'postgresql://postgres:1111@localhost:5432/quiz_db'
)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

db.init_app(app)

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(quiz_bp, url_prefix='/quiz')
app.register_blueprint(game_bp, url_prefix='/game')

with app.app_context():
    db.create_all()


@app.route('/health')
def health():
    try:
        db.session.execute(db.text('SELECT 1'))
        return jsonify({"status": "ok", "db": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "error", "db": str(e)}), 503


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    return render_template('auth.html')


@app.route('/host/<int:session_id>/<pin>')
def host_page(session_id, pin):
    return render_template('dashboard.html', session_id=session_id, pin=pin)


@app.route('/play/<pin>')
def play_page(pin):
    return render_template('play.html', pin=pin.upper())


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
