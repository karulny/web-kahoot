from flask import Blueprint, request, jsonify, session
from backend.app.middlwares.auth import login_required
from backend.app.services.quiz_service import (
    create_quiz,
    get_quiz_by_id,
    get_quizzes_by_author,
    delete_quiz,
)

quiz_bp = Blueprint('quiz', __name__)


@quiz_bp.route('/', methods=['POST'])
@login_required
def create():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Нет данных"}), 400

    title = data.get('title', '').strip()
    questions = data.get('questions', [])

    if not title:
        return jsonify({"success": False, "message": "Укажите название квиза"}), 400

    if not questions:
        return jsonify({"success": False, "message": "Добавьте хотя бы один вопрос"}), 400

    # Валидация вопросов
    for i, q in enumerate(questions):
        if not q.get('text', '').strip():
            return jsonify({"success": False, "message": f"Вопрос #{i+1}: текст не может быть пустым"}), 400
        answers = q.get('answers', [])
        if len(answers) < 2:
            return jsonify({"success": False, "message": f"Вопрос #{i+1}: нужно минимум 2 варианта ответа"}), 400
        if not any(a.get('is_correct') for a in answers):
            return jsonify({"success": False, "message": f"Вопрос #{i+1}: отметьте хотя бы один правильный ответ"}), 400

    author_id = session['user_id']
    result = create_quiz(title=title, author_id=author_id, questions_data=questions)

    if result['success']:
        return jsonify(result), 201
    return jsonify(result), 500


@quiz_bp.route('/', methods=['GET'])
@login_required
def list_quizzes():
    """GET /quiz/ — список квизов текущего пользователя"""
    author_id = session['user_id']
    result = get_quizzes_by_author(author_id)
    return jsonify(result), 200


@quiz_bp.route('/<int:quiz_id>', methods=['GET'])
@login_required
def get_one(quiz_id):
    result = get_quiz_by_id(quiz_id)
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 404


@quiz_bp.route('/<int:quiz_id>', methods=['DELETE'])
@login_required
def remove(quiz_id):
    author_id = session['user_id']
    result = delete_quiz(quiz_id=quiz_id, author_id=author_id)
    if result['success']:
        return jsonify(result), 200
    return jsonify(result), 403 if 'прав' in result.get('message', '') else 404
