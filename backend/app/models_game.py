from backend.app.db.session import db
from datetime import datetime


class GameSession(db.Model):
    __tablename__ = 'game_sessions'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    status = db.Column(db.String(20), default='waiting')  # waiting, active, finished
    current_question_index = db.Column(db.Integer, default=0)
    started_at = db.Column(db.DateTime, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)

    quiz = db.relationship('Quiz', backref='sessions')
    participants = db.relationship('SessionParticipant', backref='session', cascade='all, delete-orphan')


class SessionParticipant(db.Model):
    __tablename__ = 'session_participants'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('game_sessions.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, default=0)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    answers = db.relationship('ParticipantAnswer', backref='participant', cascade='all, delete-orphan')


class ParticipantAnswer(db.Model):
    __tablename__ = 'participant_answers'
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('session_participants.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    answer_option_id = db.Column(db.Integer, db.ForeignKey('answer_options.id'), nullable=True)
    text_answer = db.Column(db.Text, nullable=True)
    is_correct = db.Column(db.Boolean, default=False)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
