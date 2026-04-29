import random
import string
from backend.app.db.session import db
from backend.app.models import Quiz, Question, AnswerOption


def generate_pin(length=6):
    chars = string.ascii_uppercase + string.digits
    while True:
        pin = ''.join(random.choices(chars, k=length))
        if not Quiz.query.filter_by(pin_code=pin).first():
            return pin


def create_quiz(title, author_id, questions_data):
    try:
        pin = generate_pin()
        quiz = Quiz(title=title, pin_code=pin, author_id=author_id)
        db.session.add(quiz)
        db.session.flush()

        for q_data in questions_data:
            q = Question(
                text=q_data['text'],
                question_type=q_data.get('question_type', 'single'),
                media_url=q_data.get('media_url'),
                quiz_id=quiz.id
            )
            db.session.add(q)
            db.session.flush()

            db.session.bulk_save_objects([
                AnswerOption(text=a['text'], is_correct=a.get('is_correct', False), question_id=q.id)
                for a in q_data.get('answers', [])
            ])

        db.session.commit()
        return {"success": True, "quiz_id": quiz.id, "pin_code": pin}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": str(e)}


def update_quiz(quiz_id, author_id, title, questions_data):
    """Обновить квиз: заменить название и все вопросы с ответами."""
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return {"success": False, "message": "Квиз не найден"}
    if quiz.author_id != author_id:
        return {"success": False, "message": "Нет прав"}

    try:
        quiz.title = title

        # Удаляем все старые вопросы (каскад удалит и ответы)
        for q in list(quiz.questions):
            db.session.delete(q)
        db.session.flush()

        # Добавляем новые
        for q_data in questions_data:
            q = Question(
                text=q_data['text'],
                question_type=q_data.get('question_type', 'single'),
                media_url=q_data.get('media_url'),
                quiz_id=quiz.id
            )
            db.session.add(q)
            db.session.flush()

            db.session.bulk_save_objects([
                AnswerOption(text=a['text'], is_correct=a.get('is_correct', False), question_id=q.id)
                for a in q_data.get('answers', [])
            ])

        db.session.commit()
        return {"success": True, "quiz_id": quiz.id}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": str(e)}


def get_quiz_by_id(quiz_id):
    q = Quiz.query.get(quiz_id)
    if not q:
        return {"success": False, "message": "Не найден"}

    return {
        "success": True,
        "quiz": {
            "id": q.id, "title": q.title, "pin_code": q.pin_code,
            "created_at": q.created_at.isoformat(),
            "questions": [{
                "id": quest.id, "text": quest.text, "type": quest.question_type,
                "media_url": quest.media_url,
                "answers": [{"id": a.id, "text": a.text, "correct": a.is_correct} for a in quest.answers]
            } for quest in q.questions]
        }
    }


def get_quizzes_by_author(author_id):
    qs = Quiz.query.filter_by(author_id=author_id).order_by(Quiz.created_at.desc()).all()
    return {
        "success": True,
        "quizzes": [{
            "id": q.id, "title": q.title, "pin": q.pin_code,
            "date": q.created_at.isoformat(), "count": len(q.questions)
        } for q in qs]
    }


def delete_quiz(quiz_id, author_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return {"success": False, "message": "Не найден"}
    if quiz.author_id != author_id:
        return {"success": False, "message": "Нет прав"}

    try:
        db.session.delete(quiz)
        db.session.commit()
        return {"success": True}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": str(e)}
