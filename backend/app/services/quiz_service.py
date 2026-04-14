import random
import string
from backend.app.db.session import db
from backend.app.models import Quiz, Question, AnswerOption


def generate_pin(length: int = 6) -> str:
    """Генерирует уникальный pin-код для комнаты"""
    while True:
        pin = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        if not Quiz.query.filter_by(pin_code=pin).first():
            return pin


def create_quiz(title: str, author_id: int, questions_data: list) -> dict:
    try:
        pin = generate_pin()
        quiz = Quiz(title=title, pin_code=pin, author_id=author_id)
        db.session.add(quiz)
        db.session.flush()

        for q in questions_data:
            question = Question(
                text=q['text'],
                question_type=q.get('question_type', 'single'),
                media_url=q.get('media_url'),
                quiz_id=quiz.id
            )
            db.session.add(question)
            db.session.flush()

            for a in q.get('answers', []):
                answer = AnswerOption(
                    text=a['text'],
                    is_correct=a.get('is_correct', False),
                    question_id=question.id
                )
                db.session.add(answer)

        db.session.commit()
        return {"success": True, "quiz_id": quiz.id, "pin_code": pin}

    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": str(e)}


def get_quiz_by_id(quiz_id: int) -> dict:
    """Возвращает квиз со всеми вопросами и ответами"""
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return {"success": False, "message": "Квиз не найден"}

    return {
        "success": True,
        "quiz": {
            "id": quiz.id,
            "title": quiz.title,
            "pin_code": quiz.pin_code,
            "created_at": quiz.created_at.isoformat(),
            "questions": [
                {
                    "id": q.id,
                    "text": q.text,
                    "question_type": q.question_type,
                    "media_url": q.media_url,
                    "answers": [
                        {"id": a.id, "text": a.text, "is_correct": a.is_correct}
                        for a in q.answers
                    ]
                }
                for q in quiz.questions
            ]
        }
    }


def get_quizzes_by_author(author_id: int) -> dict:
    """Список всех квизов автора (без вопросов — для списка)"""
    quizzes = Quiz.query.filter_by(author_id=author_id).order_by(Quiz.created_at.desc()).all()
    return {
        "success": True,
        "quizzes": [
            {
                "id": q.id,
                "title": q.title,
                "pin_code": q.pin_code,
                "created_at": q.created_at.isoformat(),
                "questions_count": len(q.questions)
            }
            for q in quizzes
        ]
    }


def delete_quiz(quiz_id: int, author_id: int) -> dict:
    """Удаляет квиз. Проверяет, что удаляет именно автор"""
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return {"success": False, "message": "Квиз не найден"}
    if quiz.author_id != author_id:
        return {"success": False, "message": "Нет прав для удаления"}

    try:
        db.session.delete(quiz)
        db.session.commit()
        return {"success": True}
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": str(e)}
