from flask import Blueprint, request, jsonify
from backend.app.middlwares.auth import login_required
from backend.app.services.quiz_service import (
    create_quiz, get_quiz_by_id, get_quizzes_by_author, delete_quiz, update_quiz
)

quiz_bp = Blueprint('quiz', __name__)


def _validate_questions(questions):
    """Общая валидация вопросов. Возвращает строку-ошибку или None."""
    for i, q in enumerate(questions, 1):
        answers = q.get('answers', [])
        if not q.get('text', '').strip():
            return f"Вопрос {i}: пустой текст"
        if len(answers) < 2:
            return f"Вопрос {i}: минимум 2 варианта ответа"
        q_type = q.get('question_type', 'single')
        if q_type != 'poll' and not any(a.get('is_correct') for a in answers):
            return f"Вопрос {i}: нет правильного ответа"
    return None


@quiz_bp.route('/', methods=['POST'])
@login_required
def create():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    questions = data.get('questions', [])

    if not title or not questions:
        return jsonify({"success": False, "message": "Название и вопросы обязательны"}), 400

    err = _validate_questions(questions)
    if err:
        return jsonify({"success": False, "message": err}), 400

    result = create_quiz(title, request.user_id, questions)
    return jsonify(result), 201 if result['success'] else 500


@quiz_bp.route('/<int:quiz_id>', methods=['PUT'])
@login_required
def update(quiz_id):
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    questions = data.get('questions', [])

    if not title or not questions:
        return jsonify({"success": False, "message": "Название и вопросы обязательны"}), 400

    err = _validate_questions(questions)
    if err:
        return jsonify({"success": False, "message": err}), 400

    result = update_quiz(quiz_id, request.user_id, title, questions)
    return jsonify(result), 200 if result['success'] else (403 if 'прав' in result.get('message', '') else 404)


@quiz_bp.route('/', methods=['GET'])
@login_required
def list_quizzes():
    return jsonify(get_quizzes_by_author(request.user_id)), 200


@quiz_bp.route('/<int:quiz_id>', methods=['GET'])
@login_required
def get_one(quiz_id):
    result = get_quiz_by_id(quiz_id)
    return jsonify(result), 200 if result['success'] else 404


@quiz_bp.route('/<int:quiz_id>', methods=['DELETE'])
@login_required
def remove(quiz_id):
    result = delete_quiz(quiz_id, request.user_id)
    status = 200 if result['success'] else (403 if 'прав' in result.get('message', '') else 404)
    return jsonify(result), status
