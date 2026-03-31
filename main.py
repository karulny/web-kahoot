from flask import Flask
from app.models import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1111@localhost:5432/quiz_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
@app.route('/')
def hello_world():
    return 'Тест ы'

if __name__ == "__main__":
    app.run(debug=True)