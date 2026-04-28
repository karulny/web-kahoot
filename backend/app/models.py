# Инициализируем объект базы данных
from backend.app.db.session import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Тут будем хранить хэш пароля

    # Связь: один автор может создать много квизов
    quizzes = db.relationship('Quiz', backref='author', lazy=True)


class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    pin_code = db.Column(db.String(10), unique=True, nullable=False)  # Код для входа игроков
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sessions = db.relationship(
        'GameSession', cascade='all, delete-orphan', lazy=True
    )
    # Связи
    questions = db.relationship('Question', backref='quiz', cascade="all, delete-orphan", lazy=True)
    participants = db.relationship('Participant', backref='quiz', cascade="all, delete-orphan", lazy=True)


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    media_url = db.Column(db.String(255), nullable=True)
    question_type = db.Column(db.String(20), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)

    # Связь с вариантами ответов
    answers = db.relationship('AnswerOption', backref='question', cascade="all, delete-orphan", lazy=True)


class AnswerOption(db.Model):
    __tablename__ = 'answer_options'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    is_correct = db.Column(db.Boolean, default=False)  # Правильный ли это ответ
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)


class Participant(db.Model):
    __tablename__ = 'participants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, default=0)  # Итоговые баллы для выгрузки в Excel
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)