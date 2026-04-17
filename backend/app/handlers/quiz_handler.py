from flask import Blueprint, request, jsonify, session
from backend.app.middlwares.auth import login_required
from backend.app.services.quiz_service import (
    create_quiz, get_quiz_by_id, get_quizzes_by_author, delete_quiz
)

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/', methods=['POST'])
@login_required
def create():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    questions = data.get('questions', [])

    if not title or not questions:
        return jsonify({"success": False, "message": "Название и вопросы обязательны"}), 400

    for i, q in enumerate(questions, 1):
        answers = q.get('answers', [])
        if not q.get('text', '').strip():
            return jsonify({"success": False, "message": f"Вопрос {i}: пустой текст"}), 400
        if len(answers) < 2 or not any(a.get('is_correct') for a in answers):
            return jsonify({"success": False, "message": f"Вопрос {i}: неверные ответы"}), 400

    result = create_quiz(title, session['user_id'], questions)
    return jsonify(result), 201 if result['success'] else 500

@quiz_bp.route('/', methods=['GET'])
@login_required
def list_quizzes():
    return jsonify(get_quizzes_by_author(session['user_id'])), 200

@quiz_bp.route('/<int:quiz_id>', methods=['GET'])
@login_required
def get_one(quiz_id):
    result = get_quiz_by_id(quiz_id)
    return jsonify(result), 200 if result['success'] else 404

@quiz_bp.route('/<int:quiz_id>', methods=['DELETE'])
@login_required
def remove(quiz_id):
    result = delete_quiz(quiz_id, session['user_id'])
    status = 200 if result['success'] else (403 if 'прав' in result.get('message', '') else 404)
    return jsonify(result), status