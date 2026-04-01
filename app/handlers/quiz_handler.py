from flask import Blueprint, request, jsonify, render_template
from app.services.quiz_service import create_quiz_logic

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/create', methods=['POST'])
def handle_create_quiz():
    data = request.get_json()
    # Вызываем сервис
    quiz = create_quiz_logic(data['title'], author_id=1) # работает но фигня
    return jsonify({"status": "success", "pin": quiz.pin_code})

@quiz_bp.route('/join')
def join_page():
    return render_template('index.html')